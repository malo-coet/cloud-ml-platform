variable "do_token" {
  description = "DigitalOcean personal access token (read/write)."
  type        = string
  sensitive   = true
}

variable "project_name" {
  description = "Prefix used to name the created resources."
  type        = string
  default     = "cloud-ml-platform"
}

variable "region" {
  description = "DigitalOcean region slug. fra1 = Frankfurt (lowest latency from France)."
  type        = string
  default     = "fra1"
}

variable "droplet_size" {
  description = <<-EOT
    Droplet size slug. s-2vcpu-4gb (~$24/month) fits the whole stack with swap.
    Upgrade to s-4vcpu-8gb if training jobs get heavier.
  EOT
  type        = string
  default     = "s-2vcpu-4gb"
}

variable "droplet_image" {
  description = "Base OS image."
  type        = string
  default     = "ubuntu-24-04-x64"
}

variable "ssh_public_key_path" {
  description = "Public key uploaded to the droplet for SSH access."
  type        = string
  default     = "~/.ssh/id_ed25519.pub"
}

variable "ssh_source_addresses" {
  description = <<-EOT
    CIDRs allowed to reach SSH. Defaults to the whole internet because home IPs
    are dynamic; narrow it to your own IP/32 for a stricter setup.
  EOT
  type        = list(string)
  default     = ["0.0.0.0/0", "::/0"]
}
