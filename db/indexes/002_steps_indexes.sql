-- Aurora DSQL: ステップテーブルのインデックス

CREATE INDEX ASYNC IF NOT EXISTS idx_steps_tenant_task_pos
    ON steps (tenant_id, task_id, position);
