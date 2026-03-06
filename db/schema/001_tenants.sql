-- Aurora DSQL: テナントテーブル
-- 外部キー制約なし（Aurora DSQLの制約のため）

CREATE TABLE IF NOT EXISTS tenants (
    id          UUID        NOT NULL DEFAULT gen_random_uuid(),
    name        TEXT        NOT NULL,
    slug        TEXT        NOT NULL,
    plan        TEXT        NOT NULL DEFAULT 'free',
    status      TEXT        NOT NULL DEFAULT 'active',
    settings    JSONB       NOT NULL DEFAULT '{}',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (id)
);
