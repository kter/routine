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

variable "sentry_dsn_parameter_name" {
  type     = string
  default  = null
  nullable = true
}

variable "sentry_traces_sample_rate" {
  type    = number
  default = 0.1
}

variable "log_level" {
  type    = string
  default = "INFO"
}

variable "log_format" {
  type    = string
  default = "json"
}

variable "log_retention_days" {
  type    = number
  default = 30
}
