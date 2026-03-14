#!/usr/bin/env bash
# conftest-plan.sh: Terraform plan を生成して Conftest でポリシーチェックを実行する
#
# lambda.zip が存在しない場合は一時的なプレースホルダーを作成してから plan を実行し、
# 終了時に自動削除する。
# これにより、Lambdaパッケージをビルドしていない状態でも
# インフラのポリシーチェックを実行できる。
#
# Usage: bash scripts/conftest-plan.sh [ENV]
#   ENV: dev (default) | prd

set -euo pipefail

ENV="${1:-dev}"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

INFRA_DIR="$PROJECT_ROOT/infra"
LAMBDA_ZIP="$PROJECT_ROOT/lambda.zip"
PLAN_FILE="$INFRA_DIR/${ENV}.tfplan"
PLAN_JSON="/tmp/conftest-${ENV}.tfplan.json"

LAMBDA_CREATED=false

cleanup() {
  rm -f "$PLAN_JSON" "$PLAN_FILE"
  if [ "$LAMBDA_CREATED" = "true" ]; then
    rm -f "$LAMBDA_ZIP"
    echo "conftest-plan: removed temporary lambda.zip placeholder"
  fi
}
trap cleanup EXIT

# lambda.zip がなければ一時プレースホルダーを作成
if [ ! -f "$LAMBDA_ZIP" ]; then
  echo "conftest-plan: lambda.zip not found, creating temporary placeholder..."
  touch "$LAMBDA_ZIP"
  LAMBDA_CREATED=true
fi

echo "conftest-plan: running terraform plan for ENV=$ENV..."
terraform -chdir="$INFRA_DIR" workspace select "$ENV"
terraform -chdir="$INFRA_DIR" plan -out="${ENV}.tfplan"
terraform -chdir="$INFRA_DIR" show -json "${ENV}.tfplan" > "$PLAN_JSON"

echo "conftest-plan: running conftest test..."
mise exec -- conftest test "$PLAN_JSON" \
  --policy "$INFRA_DIR/policy" \
  --all-namespaces
