"""baseline schema

Revision ID: 20260311_000001
Revises:
Create Date: 2026-03-11 10:00:00
"""

from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy import inspect

from alembic import op

revision = "20260311_000001"
down_revision = None
branch_labels = None
depends_on = None


def _uuid_default() -> sa.TextClause | None:
    if op.get_bind().dialect.name == "postgresql":
        return sa.text("gen_random_uuid()")
    return None


def _create_async_index_if_needed(
    table_name: str,
    index_name: str,
    columns_sql: str,
) -> None:
    bind = op.get_bind()
    indexes = {idx["name"] for idx in inspect(bind).get_indexes(table_name)}
    if index_name in indexes:
        return

    create_index_sql = "CREATE INDEX IF NOT EXISTS"
    if bind.dialect.name == "postgresql":
        create_index_sql = "CREATE INDEX ASYNC IF NOT EXISTS"

    op.execute(f"{create_index_sql} {index_name} ON {table_name} ({columns_sql})")


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    existing_tables = set(inspector.get_table_names())

    if "tenants" not in existing_tables:
        op.create_table(
            "tenants",
            sa.Column("id", sa.Uuid(as_uuid=False), nullable=False, server_default=_uuid_default()),
            sa.Column("name", sa.Text(), nullable=False),
            sa.Column("slug", sa.Text(), nullable=False),
            sa.Column("plan", sa.Text(), nullable=False, server_default=sa.text("'free'")),
            sa.Column("status", sa.Text(), nullable=False, server_default=sa.text("'active'")),
            sa.Column("settings", sa.Text(), nullable=False, server_default=sa.text("'{}'")),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
            sa.PrimaryKeyConstraint("id"),
        )

    if "tasks" not in existing_tables:
        op.create_table(
            "tasks",
            sa.Column("id", sa.Uuid(as_uuid=False), nullable=False, server_default=_uuid_default()),
            sa.Column("tenant_id", sa.Uuid(as_uuid=False), nullable=False),
            sa.Column("title", sa.Text(), nullable=False),
            sa.Column("description", sa.Text(), nullable=False, server_default=sa.text("''")),
            sa.Column("cron_expression", sa.Text(), nullable=False),
            sa.Column(
                "timezone", sa.Text(), nullable=False, server_default=sa.text("'Asia/Tokyo'")
            ),
            sa.Column(
                "estimated_minutes", sa.Integer(), nullable=False, server_default=sa.text("30")
            ),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("TRUE")),
            sa.Column("tags", sa.Text(), nullable=False, server_default=sa.text("'[]'")),
            sa.Column("metadata", sa.Text(), nullable=False, server_default=sa.text("'{}'")),
            sa.Column("created_by", sa.Text(), nullable=False),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
            sa.PrimaryKeyConstraint("id"),
        )

    if "steps" not in existing_tables:
        op.create_table(
            "steps",
            sa.Column("id", sa.Uuid(as_uuid=False), nullable=False, server_default=_uuid_default()),
            sa.Column("tenant_id", sa.Uuid(as_uuid=False), nullable=False),
            sa.Column("task_id", sa.Uuid(as_uuid=False), nullable=False),
            sa.Column("position", sa.Integer(), nullable=False),
            sa.Column("title", sa.Text(), nullable=False),
            sa.Column("instruction", sa.Text(), nullable=False, server_default=sa.text("''")),
            sa.Column("evidence_type", sa.Text(), nullable=False, server_default=sa.text("'none'")),
            sa.Column("is_required", sa.Boolean(), nullable=False, server_default=sa.text("TRUE")),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
            sa.CheckConstraint(
                "evidence_type IN ('none', 'text', 'image')", name="ck_steps_evidence_type"
            ),
            sa.PrimaryKeyConstraint("id"),
        )

    if "executions" not in existing_tables:
        op.create_table(
            "executions",
            sa.Column("id", sa.Uuid(as_uuid=False), nullable=False, server_default=_uuid_default()),
            sa.Column("tenant_id", sa.Uuid(as_uuid=False), nullable=False),
            sa.Column("task_id", sa.Uuid(as_uuid=False), nullable=False),
            sa.Column("started_by", sa.Text(), nullable=False),
            sa.Column("status", sa.Text(), nullable=False, server_default=sa.text("'in_progress'")),
            sa.Column("scheduled_for", sa.DateTime(timezone=True), nullable=True),
            sa.Column(
                "started_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
            sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("duration_seconds", sa.Integer(), nullable=True),
            sa.Column("notes", sa.Text(), nullable=False, server_default=sa.text("''")),
            sa.Column("metadata", sa.Text(), nullable=False, server_default=sa.text("'{}'")),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
            sa.CheckConstraint(
                "status IN ('in_progress', 'completed', 'abandoned')", name="ck_executions_status"
            ),
            sa.PrimaryKeyConstraint("id"),
        )

    if "execution_steps" not in existing_tables:
        op.create_table(
            "execution_steps",
            sa.Column("id", sa.Uuid(as_uuid=False), nullable=False, server_default=_uuid_default()),
            sa.Column("tenant_id", sa.Uuid(as_uuid=False), nullable=False),
            sa.Column("execution_id", sa.Uuid(as_uuid=False), nullable=False),
            sa.Column("step_id", sa.Uuid(as_uuid=False), nullable=False),
            sa.Column("position", sa.Integer(), nullable=False),
            sa.Column("step_snapshot", sa.Text(), nullable=False),
            sa.Column("status", sa.Text(), nullable=False, server_default=sa.text("'pending'")),
            sa.Column("evidence_text", sa.Text(), nullable=True),
            sa.Column("evidence_image_key", sa.Text(), nullable=True),
            sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("completed_by", sa.Text(), nullable=True),
            sa.Column("notes", sa.Text(), nullable=False, server_default=sa.text("''")),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
            sa.CheckConstraint(
                "status IN ('pending', 'completed', 'skipped')", name="ck_execution_steps_status"
            ),
            sa.PrimaryKeyConstraint("id"),
        )

    _create_async_index_if_needed("tasks", "idx_tasks_tenant_active", "tenant_id, is_active")
    _create_async_index_if_needed(
        "steps", "idx_steps_tenant_task_pos", "tenant_id, task_id, position"
    )
    _create_async_index_if_needed("executions", "idx_executions_tenant_task", "tenant_id, task_id")
    _create_async_index_if_needed("executions", "idx_executions_tenant_status", "tenant_id, status")
    _create_async_index_if_needed(
        "executions", "idx_executions_tenant_scheduled", "tenant_id, scheduled_for"
    )
    _create_async_index_if_needed(
        "execution_steps", "idx_exec_steps_tenant_exec", "tenant_id, execution_id"
    )
    _create_async_index_if_needed(
        "execution_steps", "idx_exec_steps_exec_position", "execution_id, position"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_exec_steps_exec_position")
    op.execute("DROP INDEX IF EXISTS idx_exec_steps_tenant_exec")
    op.execute("DROP INDEX IF EXISTS idx_executions_tenant_scheduled")
    op.execute("DROP INDEX IF EXISTS idx_executions_tenant_status")
    op.execute("DROP INDEX IF EXISTS idx_executions_tenant_task")
    op.execute("DROP INDEX IF EXISTS idx_steps_tenant_task_pos")
    op.execute("DROP INDEX IF EXISTS idx_tasks_tenant_active")
    op.execute("DROP TABLE IF EXISTS execution_steps")
    op.execute("DROP TABLE IF EXISTS executions")
    op.execute("DROP TABLE IF EXISTS steps")
    op.execute("DROP TABLE IF EXISTS tasks")
    op.execute("DROP TABLE IF EXISTS tenants")
