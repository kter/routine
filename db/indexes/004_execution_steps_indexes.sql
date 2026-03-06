-- Aurora DSQL: 実行ステップテーブルのインデックス

CREATE INDEX ASYNC IF NOT EXISTS idx_exec_steps_tenant_exec
    ON execution_steps (tenant_id, execution_id);

CREATE INDEX ASYNC IF NOT EXISTS idx_exec_steps_exec_position
    ON execution_steps (execution_id, position);
