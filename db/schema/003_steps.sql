-- Aurora DSQL: ステップテーブル
-- 外部キー制約なし（Aurora DSQLの制約のため）
-- task_id はアプリ層で整合性チェック

CREATE TABLE IF NOT EXISTS steps (
    id              UUID    NOT NULL DEFAULT gen_random_uuid(),
    tenant_id       UUID    NOT NULL,
    task_id         UUID    NOT NULL,
    position        INTEGER NOT NULL,
    title           TEXT    NOT NULL,
    instruction     TEXT    NOT NULL DEFAULT '',
    evidence_type   TEXT    NOT NULL DEFAULT 'none'
        CHECK (evidence_type IN ('none', 'text', 'image')),
    is_required     BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (id)
);
