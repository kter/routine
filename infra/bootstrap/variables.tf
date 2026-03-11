variable "aws_region" {
  description = "AWS region for bootstrap resources"
  type        = string
  default     = "ap-northeast-1"
}

variable "aws_profile" {
  description = "AWS profile to use for bootstrap"
  type        = string
  default     = "default"
}

variable "state_bucket_name" {
  description = "S3 bucket name for Terraform remote state"
  type        = string
  default     = "routineops-tfstate"
}
