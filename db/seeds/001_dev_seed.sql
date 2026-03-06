-- Development seed data
-- テナントと初期タスクを作成

-- テナント作成
INSERT INTO tenants (id, name, slug, plan, status)
VALUES (
    '00000000-0000-0000-0000-000000000001',
    'Dev Tenant',
    'dev',
    'free',
    'active'
) ON CONFLICT (id) DO NOTHING;

-- タスク1: 月次セキュリティパッチ確認
INSERT INTO tasks (id, tenant_id, title, description, cron_expression, timezone, estimated_minutes, is_active, tags, created_by)
VALUES (
    '10000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '月次セキュリティパッチ確認',
    '毎月1日にAWSのセキュリティパッチ適用状況を確認する定期作業',
    '0 10 1 * *',
    'Asia/Tokyo',
    60,
    TRUE,
    ARRAY['security', 'monthly', 'aws'],
    'seed-user'
) ON CONFLICT (id) DO NOTHING;

-- ステップ1
INSERT INTO steps (id, tenant_id, task_id, position, title, instruction, evidence_type, is_required)
VALUES (
    '20000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    '10000000-0000-0000-0000-000000000001',
    1,
    'AWS Security Hub 確認',
    '## 手順\n1. AWS Console > Security Hub を開く\n2. 「Findings」タブを確認する\n3. 重大度「CRITICAL」「HIGH」の件数を記録する',
    'text',
    TRUE
) ON CONFLICT (id) DO NOTHING;

-- ステップ2
INSERT INTO steps (id, tenant_id, task_id, position, title, instruction, evidence_type, is_required)
VALUES (
    '20000000-0000-0000-0000-000000000002',
    '00000000-0000-0000-0000-000000000001',
    '10000000-0000-0000-0000-000000000001',
    2,
    'パッチ適用確認',
    '## 手順\n1. Systems Manager > Patch Manager を開く\n2. 未適用パッチの一覧を確認する\n3. 完了画面のスクリーンショットを取得する',
    'image',
    TRUE
) ON CONFLICT (id) DO NOTHING;

-- タスク2: 週次バックアップ確認
INSERT INTO tasks (id, tenant_id, title, description, cron_expression, timezone, estimated_minutes, is_active, tags, created_by)
VALUES (
    '10000000-0000-0000-0000-000000000002',
    '00000000-0000-0000-0000-000000000001',
    '週次バックアップ確認',
    '毎週月曜日にS3バックアップの確認を行う',
    '0 9 * * 1',
    'Asia/Tokyo',
    30,
    TRUE,
    ARRAY['backup', 'weekly', 'aws'],
    'seed-user'
) ON CONFLICT (id) DO NOTHING;

INSERT INTO steps (id, tenant_id, task_id, position, title, instruction, evidence_type, is_required)
VALUES (
    '20000000-0000-0000-0000-000000000003',
    '00000000-0000-0000-0000-000000000001',
    '10000000-0000-0000-0000-000000000002',
    1,
    'S3バックアップ確認',
    '1. S3コンソールを開く\n2. バックアップバケットの最新オブジェクトを確認する\n3. タイムスタンプが正常であることを記録する',
    'text',
    TRUE
) ON CONFLICT (id) DO NOTHING;
