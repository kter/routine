###############################################################################
# Lambda / CloudWatch Logs ポリシー
#
# 対象リソース:
#   - aws_lambda_function      : タイムアウト・メモリ・ランタイム
#   - aws_cloudwatch_log_group : ログ保持期間
###############################################################################

package main

import rego.v1

# CloudWatch ログ保持期間: 0 (期限なし) は禁止
deny contains msg if {
  resource := input.resource_changes[_]
  resource.type == "aws_cloudwatch_log_group"
  resource.change.after != null
  resource.change.after.retention_in_days == 0
  msg := sprintf(
    "%s: CloudWatch log_group retention_in_days must be > 0 (0 = never expire). Set an explicit retention period.",
    [resource.address],
  )
}

# Lambda タイムアウト: AWS の上限 (900秒) を超えてはいけない
deny contains msg if {
  resource := input.resource_changes[_]
  resource.type == "aws_lambda_function"
  resource.change.after != null
  resource.change.after.timeout > 900
  msg := sprintf(
    "%s: Lambda timeout %d exceeds AWS maximum of 900 seconds",
    [resource.address, resource.change.after.timeout],
  )
}

# Lambda メモリ: AWS の下限 (128 MB) を下回ってはいけない
deny contains msg if {
  resource := input.resource_changes[_]
  resource.type == "aws_lambda_function"
  resource.change.after != null
  resource.change.after.memory_size < 128
  msg := sprintf(
    "%s: Lambda memory_size %d MB is below the minimum of 128 MB",
    [resource.address, resource.change.after.memory_size],
  )
}

# Lambda ランタイム: EOL 済みランタイムは使用禁止
deprecated_runtimes := {
  "python3.8",
  "python3.9",
  "nodejs14.x",
  "nodejs16.x",
  "ruby2.7",
  "java8",
  "go1.x",
}

deny contains msg if {
  resource := input.resource_changes[_]
  resource.type == "aws_lambda_function"
  resource.change.after != null
  runtime := resource.change.after.runtime
  deprecated_runtimes[runtime]
  msg := sprintf(
    "%s: Lambda runtime '%s' is deprecated/EOL. Upgrade to a supported runtime.",
    [resource.address, runtime],
  )
}
