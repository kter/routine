###############################################################################
# Aurora DSQL Module
###############################################################################

resource "aws_dsql_cluster" "main" {
  deletion_protection_enabled = var.environment == "prd"

  tags = {
    Name        = "${var.project}-${var.environment}"
    Environment = var.environment
  }
}
