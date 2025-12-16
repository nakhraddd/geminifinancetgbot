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

    # Install dependencies
    apt-get update
    apt-get install -y git python3 python3-pip

    # Create a non-root user and grant sudo
    useradd -m -s /bin/bash gcp-user
    echo "gcp-user ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

    # Clone the repository
    git clone https://github.com/${{ github.repository }}.git /app

    # Install Python dependencies
    pip3 install -r /app/requirements.txt

    # Create systemd service
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

    # Enable and start the service
    systemctl daemon-reload
    systemctl enable telegram-bot.service
    systemctl start telegram-bot.service
  EOF

  service_account {
    scopes = ["cloud-platform"]
  }

  tags = ["http-server", "https-server"] # Add any tags you need
}
