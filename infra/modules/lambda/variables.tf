variable "project" {
  type = string
}

variable "environment" {
  type = string
}

variable "lambda_zip_path" {
  type = string
}

variable "db_cluster_endpoint" {
  type      = string
  sensitive = true
}

variable "cognito_user_pool_id" {
  type = string
}

variable "cognito_client_id" {
  type = string
}

variable "evidence_bucket_name" {
  type = string
}

variable "cors_origins" {
  type = string
}

variable "log_retention_days" {
  type    = number
  default = 30
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
