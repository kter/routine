terraform {
  required_version = ">= 1.6"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    awscc = {
      source  = "hashicorp/awscc"
      version = "~> 1.0"
    }
  }

  # S3 リモートステート
  # workspace ごとに自動でキーが分岐:
  #   dev: env:/dev/routineops/terraform.tfstate
  #   prd: env:/prd/routineops/terraform.tfstate
  backend "s3" {
    bucket         = "routineops-tfstate"
    key            = "routineops/terraform.tfstate"
    region         = "ap-northeast-1"
    dynamodb_table = "routineops-tfstate-lock"
    encrypt        = true
  }
}
