variable "aws_region" {
  description = "Primary AWS region"
  type        = string
  default     = "ap-northeast-1"
}

variable "sentry_backend_dsn_parameter_name" {
  description = "Optional SSM SecureString parameter name that stores the backend Sentry DSN"
  type        = string
  default     = null
  nullable    = true
}

variable "sentry_traces_sample_rate" {
  description = "Sentry traces sample rate for backend Lambdas"
  type        = number
  default     = 0.1
}

variable "log_level" {
  description = "Application log level for backend Lambdas"
  type        = string
  default     = "INFO"
}

variable "log_format" {
  description = "Application log format for backend Lambdas"
  type        = string
  default     = "json"
}

variable "lambda_log_retention_days" {
  description = "CloudWatch Logs retention period for backend Lambdas"
  type        = number
  default     = 30
}
