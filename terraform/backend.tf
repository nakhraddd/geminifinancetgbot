terraform {
  backend "gcs" {
    bucket  = "banded-arch-480416-q0-bucket"
    prefix  = "terraform/state"
  }
}
