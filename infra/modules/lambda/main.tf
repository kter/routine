###############################################################################
# Lambda Module: FastAPI (Mangum) on Lambda
###############################################################################

data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

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
    Statement = [
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
    ]
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
    variables = {
      ENV                  = var.environment
      DB_TYPE              = "dsql"
      DB_CLUSTER_ENDPOINT  = var.db_cluster_endpoint
      DB_NAME              = "routineops"
      AWS_REGION           = data.aws_region.current.name
      COGNITO_USER_POOL_ID = var.cognito_user_pool_id
      COGNITO_CLIENT_ID    = var.cognito_client_id
      COGNITO_JWKS_URL = "https://cognito-idp.${data.aws_region.current.name}.amazonaws.com/${var.cognito_user_pool_id}/.well-known/jwks.json"
      EVIDENCE_BUCKET_NAME = var.evidence_bucket_name
      CORS_ORIGINS         = var.cors_origins
    }
  }
}

resource "aws_cloudwatch_log_group" "api" {
  name              = "/aws/lambda/${aws_lambda_function.api.function_name}"
  retention_in_days = var.log_retention_days
}
