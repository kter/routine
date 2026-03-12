###############################################################################
# Lambda Module: FastAPI (Mangum) on Lambda
###############################################################################

data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

locals {
  sentry_enabled = var.sentry_dsn_parameter_name != null
  sentry_env = local.sentry_enabled ? {
    SENTRY_DSN_PARAMETER_NAME = var.sentry_dsn_parameter_name
    SENTRY_SEND_DEFAULT_PII   = "true"
    SENTRY_TRACES_SAMPLE_RATE = tostring(var.sentry_traces_sample_rate)
  } : {}
  sentry_policy_statements = local.sentry_enabled ? [
    {
      Effect   = "Allow"
      Action   = ["ssm:GetParameter"]
      Resource = "arn:aws:ssm:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:parameter${var.sentry_dsn_parameter_name}"
    },
  ] : []
}

# ── IAM Role ─────────────────────────────────────────────────────────────

resource "aws_iam_role" "lambda" {
  name = "${var.project}-${var.environment}-lambda"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "lambda_custom" {
  name = "${var.project}-${var.environment}-lambda-policy"
  role = aws_iam_role.lambda.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = concat(
      [
        {
          Effect = "Allow"
          Action = [
            "s3:PutObject",
            "s3:GetObject",
            "s3:DeleteObject",
          ]
          Resource = "arn:aws:s3:::${var.evidence_bucket_name}/*"
        },
        {
          Effect   = "Allow"
          Action   = ["dsql:DbConnectAdmin"]
          Resource = "*"
        },
      ],
      local.sentry_policy_statements,
    )
  })
}

# ── Lambda Function ───────────────────────────────────────────────────────

resource "aws_lambda_function" "api" {
  function_name = "${var.project}-api-${var.environment}"
  role          = aws_iam_role.lambda.arn
  handler       = "routineops.main.handler"
  runtime       = "python3.12"
  timeout       = 30
  memory_size   = 512

  filename         = var.lambda_zip_path
  source_code_hash = filebase64sha256(var.lambda_zip_path)

  environment {
    variables = merge(
      {
        ENV                  = var.environment
        DB_TYPE              = "dsql"
        DB_CLUSTER_ENDPOINT  = var.db_cluster_endpoint
        DB_NAME              = "postgres"
        COGNITO_USER_POOL_ID = var.cognito_user_pool_id
        COGNITO_CLIENT_ID    = var.cognito_client_id
        COGNITO_JWKS_URL     = "https://cognito-idp.${data.aws_region.current.name}.amazonaws.com/${var.cognito_user_pool_id}/.well-known/jwks.json"
        EVIDENCE_BUCKET_NAME = var.evidence_bucket_name
        CORS_ORIGINS         = var.cors_origins
      },
      local.sentry_env,
    )
  }
}

resource "aws_cloudwatch_log_group" "api" {
  name              = "/aws/lambda/${aws_lambda_function.api.function_name}"
  retention_in_days = var.log_retention_days
}
