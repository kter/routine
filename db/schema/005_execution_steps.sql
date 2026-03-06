-- Aurora DSQL: 実行ステップテーブル
-- 実行開始時にstepをスナップショットコピー → 後のタスク編集に影響されない監査ログ
-- 外部キー制約なし（Aurora DSQLの制約のため）

CREATE TABLE IF NOT EXISTS execution_steps (
    id                 UUID    NOT NULL DEFAULT gen_random_uuid(),
    tenant_id          UUID    NOT NULL,
    execution_id       UUID    NOT NULL,
    step_id            UUID    NOT NULL,
    position           INTEGER NOT NULL,
    step_snapshot      JSONB   NOT NULL,
    status             TEXT    NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'completed', 'skipped')),
    evidence_text      TEXT,
    evidence_image_key TEXT,
    completed_at       TIMESTAMPTZ,
    completed_by       TEXT,
    notes              TEXT    NOT NULL DEFAULT '',
    created_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (id)
);
