# OpenTofu — cloud resources

Declares the DigitalOcean resources the platform runs on:

- **Droplet** (`s-2vcpu-4gb`, Ubuntu 24.04) hosting the k3s cluster
- **Cloud firewall** allowing only SSH, HTTP, HTTPS and ICMP inbound
- **SSH key** uploaded from your local public key

```bash
cp terraform.tfvars.example terraform.tfvars   # add your DigitalOcean token
tofu init && tofu plan && tofu apply
tofu output droplet_ip
```

`tofu destroy` removes everything and stops all billing.

State files, `terraform.tfvars` and `.terraform/` are gitignored — they contain
credentials and infrastructure state.

Full walkthrough: [docs/deployment.md](../../docs/deployment.md).
