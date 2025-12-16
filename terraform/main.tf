terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "4.51.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

resource "google_compute_instance" "default" {
  name         = var.instance_name
  machine_type = var.machine_type
  zone         = var.zone

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-12"
    }
  }

  network_interface {
    network = "default"
    access_config {
      // Ephemeral IP
    }
  }

  metadata = {
    "ssh-keys" = "gcp-user:${var.ssh_public_key}"
  }

  metadata_startup_script = <<-EOF
    #!/bin/bash
    set -e

    # 1. Wait for any automatic system updates to finish (prevents locking errors)
    echo "Waiting for apt locks..."
    while fuser /var/lib/dpkg/lock >/dev/null 2>&1 ; do sleep 1; done
    while fuser /var/lib/apt/lists/lock >/dev/null 2>&1 ; do sleep 1; done

    # 2. Install dependencies
    apt-get update
    apt-get install -y git python3 python3-pip

    # 3. Clone the repository
    # Remove existing /app if it exists (fixes re-run issues)
    rm -rf /app
    git clone ${var.repo_url} /app

    # 4. Install Python dependencies
    # ERROR FIX: Debian 12 requires '--break-system-packages' for system-wide pip
    pip3 install -r /app/requirements.txt --break-system-packages

    # 5. Create systemd service
    cat <<EOT > /etc/systemd/system/telegram-bot.service
    [Unit]
    Description=Telegram Bot
    After=network.target

    [Service]
    User=gcp-user
    Group=gcp-user
    WorkingDirectory=/app
    ExecStart=/usr/bin/python3 telegram_bot.py
    Restart=always

    [Install]
    WantedBy=multi-user.target
    EOT

    # 6. Enable and start the service
    systemctl daemon-reload
    systemctl enable telegram-bot.service
    systemctl start telegram-bot.service
  EOF

  service_account {
    scopes = ["cloud-platform"]
  }

  tags = ["http-server", "https-server", "ssh"] # Add any tags you need
}

resource "google_compute_firewall" "allow-ssh" {
  name    = "tf-allow-ssh"
  network = "default"

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["ssh"]
}

