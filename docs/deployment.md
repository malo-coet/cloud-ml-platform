# Production deployment

How the platform goes from an empty DigitalOcean account to `https://mlops.mcoet.com`.

```
OpenTofu  →  droplet + firewall          (infrastructure)
Ansible   →  hardening + k3s + cert-manager  (configuration)
kubectl   →  application workloads       (deployment)
```

## Prerequisites

| What | Why |
|---|---|
| DigitalOcean account + API token (read/write) | OpenTofu creates the droplet |
| SSH key pair (`~/.ssh/id_ed25519`) | The only way into the server |
| DNS control over `mcoet.com` | Sub-domains must resolve to the droplet |
| `opentofu`, `ansible`, `kubectl` locally | The three tools used below |

```bash
brew install opentofu ansible kubernetes-cli   # macOS
```

## 1. Provision the host

```bash
cd infra/opentofu
cp terraform.tfvars.example terraform.tfvars   # add your DigitalOcean token
tofu init
tofu plan                                      # review before spending anything
tofu apply
```

Outputs include `droplet_ip` — everything below refers to it.

Default size is `s-2vcpu-4gb` (~$24/month, roughly 8 months of the $200 credit).

## 2. Point DNS at the droplet

At your registrar, create two **A records**:

| Type | Name | Value |
|---|---|---|
| A | `mlops` | `<droplet_ip>` |
| A | `*.mlops` | `<droplet_ip>` |

The wildcard covers `api.`, `mlflow.`, `minio.` and `s3.` in one record. Verify
before continuing — Let's Encrypt fails if DNS has not propagated:

```bash
dig +short mlops.mcoet.com api.mlops.mcoet.com
```

## 3. Configure the server

```bash
cd infra/ansible
ansible-galaxy collection install -r requirements.yml
cp inventory.ini.example inventory.ini        # put the droplet IP in it
ansible-playbook playbook.yml
```

This hardens the OS (deploy user, key-only SSH, UFW, Fail2Ban, unattended
upgrades), adds swap, then installs k3s and cert-manager with a Let's Encrypt
`ClusterIssuer`.

> After the first run root login is disabled — switch `ansible_user` to `deploy`
> in `inventory.ini` for every later run.

## 4. Publish the container images

Pushing to `main` runs [`publish.yml`](../.github/workflows/publish.yml), which
builds four images and pushes them to GHCR:

```
ghcr.io/malo-coet/cloud-ml-platform/{backend,frontend,training-service,mlflow}:latest
```

New GHCR packages are **private** by default. Make each one public
(package → Package settings → Change visibility) so the cluster can pull without
credentials. Alternatively create an `imagePullSecret` and reference it in the
deployments.

## 5. Create the secrets

```bash
cd infra/kubernetes
cp secrets.example.yaml secrets.yaml
openssl rand -hex 32        # generate each value
```

Fill in `POSTGRES_PASSWORD`, `JWT_SECRET_KEY`, `MINIO_ROOT_USER` and
`MINIO_ROOT_PASSWORD`, then apply it (`secrets.yaml` is gitignored):

```bash
kubectl apply -f namespace.yaml
kubectl apply -f secrets.yaml
```

## 6. Deploy the platform

```bash
kubectl apply -k infra/kubernetes/
kubectl -n mlops get pods -w
```

Certificates are issued automatically; watch them settle:

```bash
kubectl -n mlops get certificate
kubectl -n mlops describe certificate platform-tls   # if it stays not-ready
```

## 7. Verify

| URL | Expected |
|---|---|
| `https://mlops.mcoet.com` | Dashboard sign-in |
| `https://api.mlops.mcoet.com/api/docs` | Swagger UI |
| `https://mlflow.mlops.mcoet.com` | MLflow |
| `https://minio.mlops.mcoet.com` | MinIO console |

Register the first account (it becomes admin), upload a CSV and start a training
run — the same flow as local development.

## Running kubectl from your laptop

The Kubernetes API is not exposed publicly. Tunnel it over SSH:

```bash
scp deploy@<droplet_ip>:~/.kube/config ./kubeconfig
sed -i '' "s/127.0.0.1/<droplet_ip>/" kubeconfig     # macOS sed
ssh -fN -L 6443:127.0.0.1:6443 deploy@<droplet_ip>
KUBECONFIG=./kubeconfig kubectl -n mlops get pods
```

Or simply run commands on the host: `ssh deploy@<droplet_ip> kubectl -n mlops get pods`.

## Day-to-day operations

```bash
kubectl -n mlops logs -f deploy/backend           # follow a service
kubectl -n mlops rollout restart deploy/backend   # pick up a new :latest image
kubectl -n mlops get pvc                          # storage usage
kubectl top nodes                                 # resource pressure
```

## Tearing everything down

Stops all billing (the droplet is the only paid resource):

```bash
cd infra/opentofu && tofu destroy
```
