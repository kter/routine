###############################################################################
# Cognito Module: User Pool + App Client + PostConfirmation Lambda
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

# ── PostConfirmation Lambda IAM Role ────────────────────────────────────────

resource "aws_iam_role" "post_confirmation" {
  name = "${var.project}-${var.environment}-post-confirmation"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "post_confirmation_basic" {
  role       = aws_iam_role.post_confirmation.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "post_confirmation_custom" {
  name = "${var.project}-${var.environment}-post-confirmation-policy"
  role = aws_iam_role.post_confirmation.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = concat(
      [
        {
          Effect   = "Allow"
          Action   = ["dsql:DbConnectAdmin"]
          Resource = "*"
        },
        {
          Effect   = "Allow"
          Action   = ["cognito-idp:AdminUpdateUserAttributes"]
          Resource = "arn:aws:cognito-idp:${var.aws_region}:${data.aws_caller_identity.current.account_id}:userpool/*"
        },
      ],
      local.sentry_policy_statements,
    )
  })
}

# ── PostConfirmation Lambda Function ────────────────────────────────────────

resource "aws_lambda_function" "post_confirmation" {
  function_name = "${var.project}-post-confirmation-${var.environment}"
  role          = aws_iam_role.post_confirmation.arn
  handler       = "routineops.infrastructure.auth.post_confirmation_trigger.handler"
  runtime       = "python3.12"
  timeout       = 30
  memory_size   = 256

  filename         = var.lambda_zip_path
  source_code_hash = filebase64sha256(var.lambda_zip_path)

  environment {
    variables = merge(
      {
        ENV                 = var.environment
        DB_CLUSTER_ENDPOINT = var.db_cluster_endpoint
        DB_NAME             = "postgres"
      },
      local.sentry_env,
    )
  }
}

resource "aws_cloudwatch_log_group" "post_confirmation" {
  name              = "/aws/lambda/${aws_lambda_function.post_confirmation.function_name}"
  retention_in_days = 30
}

resource "aws_lambda_permission" "cognito_invoke" {
  statement_id  = "AllowCognitoInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.post_confirmation.function_name
  principal     = "cognito-idp.amazonaws.com"
  source_arn    = "arn:aws:cognito-idp:${var.aws_region}:${data.aws_caller_identity.current.account_id}:userpool/*"
}

# ── User Pool ───────────────────────────────────────────────────────────────

resource "aws_cognito_user_pool" "main" {
  name = "${var.project}-${var.environment}"

  username_attributes      = ["email"]
  auto_verified_attributes = ["email"]

  password_policy {
    minimum_length    = 8
    require_lowercase = true
    require_numbers   = true
    require_uppercase = true
    require_symbols   = false
  }

  schema {
    name                = "tenant_id"
    attribute_data_type = "String"
    mutable             = true

    string_attribute_constraints {
      min_length = 36
      max_length = 36
    }
  }

  lambda_config {
    post_confirmation = aws_lambda_function.post_confirmation.arn
  }

  tags = {
    Name = "${var.project}-${var.environment}-user-pool"
  }

  depends_on = [aws_lambda_permission.cognito_invoke]
}

resource "aws_cognito_user_pool_client" "main" {
  name         = "${var.project}-${var.environment}-client"
  user_pool_id = aws_cognito_user_pool.main.id

  generate_secret                      = false
  explicit_auth_flows                  = ["ALLOW_USER_SRP_AUTH", "ALLOW_REFRESH_TOKEN_AUTH"]
  prevent_user_existence_errors        = "ENABLED"
  enable_token_revocation              = true
  allowed_oauth_flows_user_pool_client = false

  access_token_validity  = 1
  id_token_validity      = 1
  refresh_token_validity = 30

  token_validity_units {
    access_token  = "hours"
    id_token      = "hours"
    refresh_token = "days"
  }
}
