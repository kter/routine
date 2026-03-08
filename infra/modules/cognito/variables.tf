variable "project" {
  type = string
}

variable "environment" {
  type = string
}

variable "api_domain" {
  type = string
}

variable "lambda_zip_path" {
  type = string
}

variable "db_cluster_endpoint" {
  type      = string
  sensitive = true
}

variable "aws_region" {
  type = string
}
