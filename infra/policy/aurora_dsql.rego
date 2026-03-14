###############################################################################
# Aurora DSQL ポリシー
#
# 対象リソース:
#   - awscc_dsql_cluster : 削除保護設定
#
# awscc プロバイダーでは tags は [{key: ..., value: ...}] 形式のリストになる。
###############################################################################

package main

import rego.v1

# Aurora DSQL: 本番環境 (Environment=prd) では削除保護が必須
deny contains msg if {
  resource := input.resource_changes[_]
  resource.type == "awscc_dsql_cluster"
  resource.change.after != null

  # tags リストから Environment=prd を検索
  tags := resource.change.after.tags
  tag := tags[_]
  tag.key == "Environment"
  tag.value == "prd"

  not resource.change.after.deletion_protection_enabled

  msg := sprintf(
    "%s: Aurora DSQL deletion_protection_enabled must be true in the prd environment",
    [resource.address],
  )
}

# Aurora DSQL: Name タグが設定されているか確認 (warn)
warn contains msg if {
  resource := input.resource_changes[_]
  resource.type == "awscc_dsql_cluster"
  resource.change.after != null

  tags := resource.change.after.tags
  name_tags := [t | t := tags[_]; t.key == "Name"]
  count(name_tags) == 0

  msg := sprintf(
    "%s: Aurora DSQL cluster should have a Name tag for identification",
    [resource.address],
  )
}
