output "api_endpoint" {
  value = "https://${var.api_domain}"
}

output "api_gateway_id" {
  value = aws_apigatewayv2_api.main.id
}
