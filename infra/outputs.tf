output "frontend_url" {
  description = "Frontend SPA URL"
  value       = "https://${local.config.frontend_domain}"
}

output "api_url" {
  description = "API Gateway URL"
  value       = "https://${local.config.api_domain}"
}

output "cognito_user_pool_id" {
  description = "Cognito User Pool ID"
  value       = module.cognito.user_pool_id
}

output "cognito_client_id" {
  description = "Cognito App Client ID"
  value       = module.cognito.client_id
}

output "frontend_bucket_name" {
  description = "S3 bucket for frontend SPA"
  value       = module.frontend.bucket_name
}

output "cloudfront_distribution_id" {
  description = "CloudFront distribution ID"
  value       = module.frontend.cloudfront_distribution_id
}

output "aurora_dsql_cluster_endpoint" {
  description = "Aurora DSQL cluster endpoint"
  value       = module.aurora_dsql.cluster_endpoint
  sensitive   = true
}

output "evidence_bucket_name" {
  description = "S3 bucket for evidence files"
  value       = module.evidence_storage.bucket_name
}
