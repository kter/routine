###############################################################################
# S3 セキュリティポリシー
#
# 対象リソース:
#   - aws_s3_bucket_public_access_block   : パブリックアクセスブロック
#   - aws_s3_bucket_server_side_encryption_configuration : 暗号化
###############################################################################

package main

import rego.v1

# S3 パブリックアクセスブロック: block_public_acls
deny contains msg if {
  resource := input.resource_changes[_]
  resource.type == "aws_s3_bucket_public_access_block"
  resource.change.after != null
  not resource.change.after.block_public_acls
  msg := sprintf("%s: block_public_acls must be true", [resource.address])
}

# S3 パブリックアクセスブロック: block_public_policy
deny contains msg if {
  resource := input.resource_changes[_]
  resource.type == "aws_s3_bucket_public_access_block"
  resource.change.after != null
  not resource.change.after.block_public_policy
  msg := sprintf("%s: block_public_policy must be true", [resource.address])
}

# S3 パブリックアクセスブロック: ignore_public_acls
deny contains msg if {
  resource := input.resource_changes[_]
  resource.type == "aws_s3_bucket_public_access_block"
  resource.change.after != null
  not resource.change.after.ignore_public_acls
  msg := sprintf("%s: ignore_public_acls must be true", [resource.address])
}

# S3 パブリックアクセスブロック: restrict_public_buckets
deny contains msg if {
  resource := input.resource_changes[_]
  resource.type == "aws_s3_bucket_public_access_block"
  resource.change.after != null
  not resource.change.after.restrict_public_buckets
  msg := sprintf("%s: restrict_public_buckets must be true", [resource.address])
}

# S3 サーバーサイド暗号化: AES256 または aws:kms のみ許可
deny contains msg if {
  resource := input.resource_changes[_]
  resource.type == "aws_s3_bucket_server_side_encryption_configuration"
  resource.change.after != null
  rule := resource.change.after.rule[_]
  sse := rule.apply_server_side_encryption_by_default[_]
  sse.sse_algorithm != "AES256"
  sse.sse_algorithm != "aws:kms"
  msg := sprintf("%s: S3 SSE algorithm must be AES256 or aws:kms, got '%s'", [resource.address, sse.sse_algorithm])
}
