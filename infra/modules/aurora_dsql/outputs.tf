output "cluster_endpoint" {
  value     = aws_dsql_cluster.main.endpoint
  sensitive = true
}

output "cluster_arn" {
  value = aws_dsql_cluster.main.arn
}
