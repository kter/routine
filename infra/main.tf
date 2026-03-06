###############################################################################
# Root module: Workspace × AWSプロファイル切り替え + モジュール呼び出し
###############################################################################

locals {
  workspace_config = {
    dev = {
      aws_profile      = "dev"
      frontend_domain  = "routine.dev.devtools.site"
      api_domain       = "api.routine.dev.devtools.site"
      hosted_zone_name = "dev.devtools.site."
    }
    prd = {
      aws_profile      = "prd"
      frontend_domain  = "routine.devtools.site"
      api_domain       = "api.routine.devtools.site"
      hosted_zone_name = "devtools.site."
    }
  }

  config = local.workspace_config[terraform.workspace]

  common_tags = {
    Project     = "routineops"
    Environment = terraform.workspace
    ManagedBy   = "terraform"
  }
}

# ── Primary provider (ap-northeast-1) ──────────────────────────────────────

provider "aws" {
  region  = var.aws_region
  profile = local.config.aws_profile
  default_tags {
    tags = local.common_tags
  }
}

# ── CloudFront用 ACM は us-east-1 必須 ────────────────────────────────────

provider "aws" {
  alias   = "us_east_1"
  region  = "us-east-1"
  profile = local.config.aws_profile
  default_tags {
    tags = local.common_tags
  }
}

# ── awscc provider (Aurora DSQL identifier取得用) ───────────────────────

provider "awscc" {
  region  = var.aws_region
  profile = local.config.aws_profile
}

# ── Route53 ホストゾーン（既存リソースを参照） ──────────────────────────

data "aws_route53_zone" "zone" {
  name = local.config.hosted_zone_name
}

# ── Modules ───────────────────────────────────────────────────────────────

module "cognito" {
  source = "./modules/cognito"

  project     = "routineops"
  environment = terraform.workspace
  api_domain  = local.config.api_domain
}

module "aurora_dsql" {
  source = "./modules/aurora_dsql"

  project     = "routineops"
  environment = terraform.workspace
  aws_region  = var.aws_region

  providers = {
    awscc = awscc
  }
}

module "evidence_storage" {
  source = "./modules/evidence_storage"

  project     = "routineops"
  environment = terraform.workspace
}

module "lambda" {
  source = "./modules/lambda"

  project              = "routineops"
  environment          = terraform.workspace
  lambda_zip_path      = "${path.root}/../lambda.zip"
  db_cluster_endpoint  = module.aurora_dsql.cluster_endpoint
  cognito_user_pool_id = module.cognito.user_pool_id
  cognito_client_id    = module.cognito.client_id
  evidence_bucket_name = module.evidence_storage.bucket_name
  cors_origins         = "https://${local.config.frontend_domain}"
}

module "api_gateway" {
  source = "./modules/api_gateway"

  project         = "routineops"
  environment     = terraform.workspace
  lambda_arn      = module.lambda.function_arn
  lambda_invoke_arn = module.lambda.invoke_arn
  api_domain      = local.config.api_domain
  hosted_zone_id  = data.aws_route53_zone.zone.zone_id
  aws_region      = var.aws_region

  providers = {
    aws           = aws
    aws.us_east_1 = aws.us_east_1
  }
}

module "frontend" {
  source = "./modules/frontend"

  project          = "routineops"
  environment      = terraform.workspace
  frontend_domain  = local.config.frontend_domain
  hosted_zone_id   = data.aws_route53_zone.zone.zone_id

  providers = {
    aws           = aws
    aws.us_east_1 = aws.us_east_1
  }
}
