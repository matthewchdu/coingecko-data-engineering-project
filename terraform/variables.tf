variable "region" {
  type = string
    default = "europe-west2"
}
variable "projName" {
  type = string
    default = "coingecko-505717"
}
variable "USER-KEY" {
  type = string
    default = "USER_KEY.json"
}

variable "bq_dataset_name" {
  description = "The name of the BigQuery dataset for crypto data"
  type        = string
  default     = "crypto_bucket"
}