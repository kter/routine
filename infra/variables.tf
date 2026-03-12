variable "aws_region" {
  description = "Primary AWS region"
  type        = string
  default     = "ap-northeast-1"
}

variable "sentry_dsn" {
  description = "Optional Sentry DSN for Lambda monitoring"
  type        = string
  default     = null
  sensitive   = true
  nullable    = true
}

variable "sentry_traces_sample_rate" {
  description = "Sentry traces sample rate for backend Lambdas"
  type        = number
  default     = 0.1
}
