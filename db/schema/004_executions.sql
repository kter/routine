-- Aurora DSQL: 実行テーブル
-- 外部キー制約なし（Aurora DSQLの制約のため）
-- task_id はアプリ層で整合性チェック

CREATE TABLE IF NOT EXISTS executions (
    id               UUID    NOT NULL DEFAULT gen_random_uuid(),
    tenant_id        UUID    NOT NULL,
    task_id          UUID    NOT NULL,
    started_by       TEXT    NOT NULL,
    status           TEXT    NOT NULL DEFAULT 'in_progress'
        CHECK (status IN ('in_progress', 'completed', 'abandoned')),
    scheduled_for    TIMESTAMPTZ,
    started_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at     TIMESTAMPTZ,
    duration_seconds INTEGER,
    notes            TEXT    NOT NULL DEFAULT '',
    metadata         TEXT   NOT NULL DEFAULT '{}',
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (id)
);
