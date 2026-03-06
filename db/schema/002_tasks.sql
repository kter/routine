-- Aurora DSQL: タスクテーブル
-- 外部キー制約なし（Aurora DSQLの制約のため）
-- tenant_id はアプリ層で整合性チェック

CREATE TABLE IF NOT EXISTS tasks (
    id                  UUID        NOT NULL DEFAULT gen_random_uuid(),
    tenant_id           UUID        NOT NULL,
    title               TEXT        NOT NULL,
    description         TEXT        NOT NULL DEFAULT '',
    cron_expression     TEXT        NOT NULL,
    timezone            TEXT        NOT NULL DEFAULT 'Asia/Tokyo',
    estimated_minutes   INTEGER     NOT NULL DEFAULT 30,
    is_active           BOOLEAN     NOT NULL DEFAULT TRUE,
    tags                TEXT[]      NOT NULL DEFAULT '{}',
    metadata            JSONB       NOT NULL DEFAULT '{}',
    created_by          TEXT        NOT NULL,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (id)
);
