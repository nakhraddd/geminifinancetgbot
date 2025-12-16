variable "project_id" {
  description = "The GCP project ID to deploy to."
  type        = string
}

variable "region" {
  description = "The GCP region to deploy to."
  type        = string
  default     = "us-central1"
}

variable "zone" {
  description = "The GCP zone to deploy to."
  type        = string
  default     = "us-central1-a"
}

variable "instance_name" {
  description = "The name of the VM instance."
  type        = string
  default     = "telegram-bot-instance"
}

variable "machine_type" {
  description = "The machine type for the VM."
  type        = string
  default     = "e2-small"
}

variable "image_project" {
  description = "The project for the Debian 12 image."
  type        = string
  default     = "debian-cloud"
}

variable "image_family" {
  description = "The image family for Debian 12."
  type        = string
  default     = "debian-12"
}

variable "ssh_public_key" {
  description = "The SSH public key to add to the VM."
  type        = string
  sensitive   = true
}
