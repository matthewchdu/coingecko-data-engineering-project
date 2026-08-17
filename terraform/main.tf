resource "google_storage_bucket" "crypto_bucket" {
  name          = "${var.projName}-crypto-bucket"
  location      = var.region
  force_destroy = true

  lifecycle_rule {
    condition {
      age = 3
    }
    action {
      type = "Delete"
    }
  }

  lifecycle_rule {
    condition {
      age = 1
    }
    action {
      type = "AbortIncompleteMultipartUpload"
    }
  }
}

provider "google" {
  credentials = file(var.USER-KEY)
  project     = var.projName
  region      = var.region
}

resource "google_bigquery_dataset" "raw_dataset" {
  dataset_id = var.bq_dataset_name
  location   = var.region
}