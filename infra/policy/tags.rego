###############################################################################
# 必須タグポリシー
#
# root モジュールで provider "aws" の default_tags に以下を設定済み:
#   Project, Environment, ManagedBy
#
# terraform show -json の plan では、default_tags はリソースの tags_all に
# マージされて出力されるため、tags_all で検証する。
# タグ設定漏れはデプロイ後のコスト分析・環境識別に支障をきたすため warn とする。
###############################################################################

package main

import rego.v1

required_tags := {"Project", "Environment", "ManagedBy"}

# タグ付け対象リソースタイプ
taggable_types := {
  "aws_s3_bucket",
  "aws_lambda_function",
  "aws_cloudwatch_log_group",
  "aws_cognito_user_pool",
  "aws_cloudfront_distribution",
  "aws_apigatewayv2_api",
}

warn contains msg if {
  resource := input.resource_changes[_]
  taggable_types[resource.type]
  resource.change.after != null
  tags := resource.change.after.tags_all
  missing := required_tags - {k | tags[k]}
  count(missing) > 0
  msg := sprintf(
    "%s: missing required tags: %v (check provider default_tags in main.tf)",
    [resource.address, missing],
  )
}
