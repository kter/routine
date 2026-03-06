###############################################################################
# Aurora DSQL Module
###############################################################################

terraform {
  required_providers {
    awscc = {
      source = "hashicorp/awscc"
    }
  }
}

resource "awscc_dsql_cluster" "main" {
  deletion_protection_enabled = var.environment == "prd"

  tags = [
    { key = "Name", value = "${var.project}-${var.environment}" },
    { key = "Environment", value = var.environment },
  ]
}
