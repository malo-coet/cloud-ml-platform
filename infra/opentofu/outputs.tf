output "droplet_ip" {
  description = "Public IPv4 of the host — point your DNS records at this."
  value       = digitalocean_droplet.platform.ipv4_address
}

output "ssh_command" {
  description = "Connect to the freshly created droplet (before Ansible runs)."
  value       = "ssh root@${digitalocean_droplet.platform.ipv4_address}"
}

output "dns_records_to_create" {
  description = "DNS records to add at your registrar."
  value = {
    "mlops.mcoet.com"   = digitalocean_droplet.platform.ipv4_address
    "*.mlops.mcoet.com" = digitalocean_droplet.platform.ipv4_address
  }
}

output "ansible_inventory" {
  description = "Paste into infra/ansible/inventory.ini."
  value       = "[platform]\n${digitalocean_droplet.platform.ipv4_address} ansible_user=root"
}
