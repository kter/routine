###############################################################################
# CORS ワイルドカード警告ポリシー
#
# 現状の問題:
#   - api_gateway/main.tf: allow_origins = ["*"] がハードコード済み
#   - evidence_storage/main.tf: allowed_origins のデフォルトが ["*"]
#
# 本番環境でもワイルドカードが設定されていると、任意のオリジンから
# APIへのクロスオリジンリクエストが許可される。
# → deny ではなく warn として運用し、本番適用前に必ず確認すること。
###############################################################################

package main

import rego.v1

# API Gateway: CORS allow_origins にワイルドカードが含まれる場合は警告
warn contains msg if {
  resource := input.resource_changes[_]
  resource.type == "aws_apigatewayv2_api"
  resource.change.after != null
  cors := resource.change.after.cors_configuration[_]
  cors.allow_origins[_] == "*"
  msg := sprintf(
    "%s: API Gateway CORS allow_origins contains '*'. Restrict to the frontend domain in production (e.g. https://routine.devtools.site).",
    [resource.address],
  )
}

# S3 CORS: allowed_origins にワイルドカードが含まれる場合は警告
warn contains msg if {
  resource := input.resource_changes[_]
  resource.type == "aws_s3_bucket_cors_configuration"
  resource.change.after != null
  rule := resource.change.after.cors_rule[_]
  rule.allowed_origins[_] == "*"
  msg := sprintf(
    "%s: S3 CORS allowed_origins contains '*'. Restrict to the frontend domain for direct upload endpoints.",
    [resource.address],
  )
}
