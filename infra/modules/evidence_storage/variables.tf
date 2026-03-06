variable "project" {
  type = string
}

variable "environment" {
  type = string
}

variable "evidence_retention_days" {
  type    = number
  default = 365
}

variable "allowed_origins" {
  type    = list(string)
  default = ["*"]
}
