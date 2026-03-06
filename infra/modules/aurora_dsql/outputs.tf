output "cluster_endpoint" {
  # Aurora DSQL endpoint format: <cluster-id>.dsql.<region>.on.aws
  value     = "${awscc_dsql_cluster.main.identifier}.dsql.${var.aws_region}.on.aws"
  sensitive = true
}
