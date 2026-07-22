# Ansible — server configuration

Turns a bare Ubuntu droplet into a hardened k3s host. Idempotent: safe to re-run.

| Task file | What it does |
|---|---|
| `tasks/hardening.yml` | `deploy` user, key-only SSH (root login disabled), UFW, Fail2Ban, unattended security upgrades |
| `tasks/swap.yml` | 2 GB swapfile so the 4 GB host survives simultaneous service starts |
| `tasks/k3s.yml` | Pinned k3s install (Traefik included) + cert-manager and a Let's Encrypt `ClusterIssuer` |

```bash
ansible-galaxy collection install -r requirements.yml
cp inventory.ini.example inventory.ini    # add the droplet IP
ansible-playbook playbook.yml
```

Run a single stage with tags: `ansible-playbook playbook.yml --tags k3s`.

> The first run connects as `root`; it then disables root login, so later runs
> must use `ansible_user=deploy`.

Versions and the Let's Encrypt address live in `group_vars/all.yml`.

Full walkthrough: [docs/deployment.md](../../docs/deployment.md).
