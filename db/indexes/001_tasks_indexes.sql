-- Aurora DSQL: タスクテーブルのインデックス
-- CREATE INDEX ASYNC: 別トランザクションで実行（Aurora DSQL の制約）

CREATE INDEX ASYNC IF NOT EXISTS idx_tasks_tenant_active
    ON tasks (tenant_id, is_active);
