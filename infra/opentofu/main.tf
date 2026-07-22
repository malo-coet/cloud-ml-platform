# Single-node host running k3s. Everything the platform needs lives on this
# droplet; see infra/ansible for its configuration and infra/kubernetes for the
# workloads.

resource "digitalocean_ssh_key" "admin" {
  name       = "${var.project_name}-admin"
  public_key = file(pathexpand(var.ssh_public_key_path))
}

resource "digitalocean_droplet" "platform" {
  name     = var.project_name
  image    = var.droplet_image
  size     = var.droplet_size
  region   = var.region
  ssh_keys = [digitalocean_ssh_key.admin.fingerprint]

  # Free metrics agent — feeds the DigitalOcean dashboard graphs
  monitoring = true
  ipv6       = true

  tags = ["cloud-ml-platform", "k3s"]
}

# Cloud firewall — a first line of defence in front of the host's own UFW rules.
resource "digitalocean_firewall" "platform" {
  name        = "${var.project_name}-firewall"
  droplet_ids = [digitalocean_droplet.platform.id]

  inbound_rule {
    protocol         = "tcp"
    port_range       = "22"
    source_addresses = var.ssh_source_addresses
  }

  inbound_rule {
    protocol         = "tcp"
    port_range       = "80"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }

  inbound_rule {
    protocol         = "tcp"
    port_range       = "443"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }

  # ICMP so the host answers ping (useful when debugging DNS/routing)
  inbound_rule {
    protocol         = "icmp"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }

  # Unrestricted egress: package installs, Let's Encrypt, container registries
  outbound_rule {
    protocol              = "tcp"
    port_range            = "1-65535"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }

  outbound_rule {
    protocol              = "udp"
    port_range            = "1-65535"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }

  outbound_rule {
    protocol              = "icmp"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }
}
