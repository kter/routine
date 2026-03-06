-- Aurora DSQL: 実行テーブルのインデックス

CREATE INDEX ASYNC IF NOT EXISTS idx_executions_tenant_task
    ON executions (tenant_id, task_id);

CREATE INDEX ASYNC IF NOT EXISTS idx_executions_tenant_status
    ON executions (tenant_id, status);

CREATE INDEX ASYNC IF NOT EXISTS idx_executions_tenant_scheduled
    ON executions (tenant_id, scheduled_for);
