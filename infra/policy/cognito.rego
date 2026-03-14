###############################################################################
# Cognito セキュリティポリシー
#
# 対象リソース:
#   - aws_cognito_user_pool        : パスワードポリシー
#   - aws_cognito_user_pool_client : セキュリティ設定
###############################################################################

package main

import rego.v1

# Cognito User Pool クライアント: ユーザー存在確認エラーの隠蔽
# ENABLED にしないとメールアドレスの存在確認攻撃 (user enumeration) が可能になる
deny contains msg if {
  resource := input.resource_changes[_]
  resource.type == "aws_cognito_user_pool_client"
  resource.change.after != null
  resource.change.after.prevent_user_existence_errors != "ENABLED"
  msg := sprintf(
    "%s: prevent_user_existence_errors must be ENABLED to prevent user enumeration attacks",
    [resource.address],
  )
}

# Cognito User Pool クライアント: トークン失効機能の有効化
deny contains msg if {
  resource := input.resource_changes[_]
  resource.type == "aws_cognito_user_pool_client"
  resource.change.after != null
  not resource.change.after.enable_token_revocation
  msg := sprintf(
    "%s: enable_token_revocation must be true to support secure logout",
    [resource.address],
  )
}

# Cognito User Pool: パスワード最小長 8文字以上
deny contains msg if {
  resource := input.resource_changes[_]
  resource.type == "aws_cognito_user_pool"
  resource.change.after != null
  policy := resource.change.after.password_policy[_]
  policy.minimum_length < 8
  msg := sprintf(
    "%s: Cognito password minimum_length must be >= 8, got %d",
    [resource.address, policy.minimum_length],
  )
}

# Cognito User Pool: パスワードに大文字を必須化
deny contains msg if {
  resource := input.resource_changes[_]
  resource.type == "aws_cognito_user_pool"
  resource.change.after != null
  policy := resource.change.after.password_policy[_]
  not policy.require_uppercase
  msg := sprintf("%s: Cognito password policy must require uppercase letters", [resource.address])
}

# Cognito User Pool: パスワードに小文字を必須化
deny contains msg if {
  resource := input.resource_changes[_]
  resource.type == "aws_cognito_user_pool"
  resource.change.after != null
  policy := resource.change.after.password_policy[_]
  not policy.require_lowercase
  msg := sprintf("%s: Cognito password policy must require lowercase letters", [resource.address])
}

# Cognito User Pool: パスワードに数字を必須化
deny contains msg if {
  resource := input.resource_changes[_]
  resource.type == "aws_cognito_user_pool"
  resource.change.after != null
  policy := resource.change.after.password_policy[_]
  not policy.require_numbers
  msg := sprintf("%s: Cognito password policy must require numbers", [resource.address])
}
