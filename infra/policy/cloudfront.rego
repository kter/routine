###############################################################################
# CloudFront セキュリティポリシー
#
# 対象リソース:
#   - aws_cloudfront_distribution          : TLS・HTTPSリダイレクト
#   - aws_cloudfront_origin_access_control : OAC sigv4署名設定
#   - aws_apigatewayv2_domain_name         : API Gateway TLSポリシー
###############################################################################

package main

import rego.v1

# CloudFront: HTTP → HTTPS リダイレクト必須
deny contains msg if {
  resource := input.resource_changes[_]
  resource.type == "aws_cloudfront_distribution"
  resource.change.after != null
  behavior := resource.change.after.default_cache_behavior[_]
  behavior.viewer_protocol_policy != "redirect-to-https"
  behavior.viewer_protocol_policy != "https-only"
  msg := sprintf(
    "%s: CloudFront viewer_protocol_policy must be 'redirect-to-https' or 'https-only', got '%s'",
    [resource.address, behavior.viewer_protocol_policy],
  )
}

# CloudFront: TLS最小バージョン TLSv1.2_2021 必須
deny contains msg if {
  resource := input.resource_changes[_]
  resource.type == "aws_cloudfront_distribution"
  resource.change.after != null
  cert := resource.change.after.viewer_certificate[_]

  # カスタム証明書を使う場合のみチェック（デフォルトCloudFront証明書はスキップ）
  cert.acm_certificate_arn != null
  cert.minimum_protocol_version != "TLSv1.2_2021"
  cert.minimum_protocol_version != "TLSv1.2_2019"

  msg := sprintf(
    "%s: CloudFront minimum_protocol_version must be TLSv1.2_2021 or TLSv1.2_2019, got '%s'",
    [resource.address, cert.minimum_protocol_version],
  )
}

# CloudFront OAC: 署名動作は always 必須
deny contains msg if {
  resource := input.resource_changes[_]
  resource.type == "aws_cloudfront_origin_access_control"
  resource.change.after != null
  resource.change.after.signing_behavior != "always"
  msg := sprintf(
    "%s: CloudFront OAC signing_behavior must be 'always', got '%s'",
    [resource.address, resource.change.after.signing_behavior],
  )
}

# CloudFront OAC: 署名プロトコルは sigv4 必須
deny contains msg if {
  resource := input.resource_changes[_]
  resource.type == "aws_cloudfront_origin_access_control"
  resource.change.after != null
  resource.change.after.signing_protocol != "sigv4"
  msg := sprintf(
    "%s: CloudFront OAC signing_protocol must be 'sigv4', got '%s'",
    [resource.address, resource.change.after.signing_protocol],
  )
}

# API Gateway カスタムドメイン: TLS 1.2 ポリシー必須
deny contains msg if {
  resource := input.resource_changes[_]
  resource.type == "aws_apigatewayv2_domain_name"
  resource.change.after != null
  cfg := resource.change.after.domain_name_configuration[_]
  cfg.security_policy != "TLS_1_2"
  msg := sprintf(
    "%s: API Gateway domain security_policy must be TLS_1_2, got '%s'",
    [resource.address, cfg.security_policy],
  )
}
