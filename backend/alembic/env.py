from __future__ import annotations

import os
import sys
from pathlib import Path

from sqlalchemy.engine import Connection, Engine

from alembic import context

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from routineops.infrastructure.db import models as _models  # noqa: F401, E402
from routineops.infrastructure.db.base import Base  # noqa: E402
from routineops.infrastructure.db.engine import (  # noqa: E402
    create_dsql_engine,
    create_sqlite_engine,
)

config = context.config
target_metadata = Base.metadata


def _find_cluster_endpoint(environment: str, region: str) -> str:
    import boto3

    client = boto3.client("dsql", region_name=region)
    expected_name = f"routineops-{environment}"

    paginator = client.get_paginator("list_clusters")
    for page in paginator.paginate():
        for cluster in page.get("clusters", []):
            details = client.get_cluster(identifier=cluster["identifier"])
            tags = details.get("tags", {})
            if tags.get("Environment") == environment and tags.get("Name") == expected_name:
                endpoint = details.get("endpoint")
                if endpoint:
                    return endpoint

    raise RuntimeError(f"Could not find DSQL cluster for ENV={environment}")


def _get_engine() -> Engine:
    db_type = os.getenv("DB_TYPE", "dsql")
    if db_type == "sqlite":
        db_path = os.getenv("SQLITE_PATH", ":memory:")
        return create_sqlite_engine(db_path)

    endpoint = os.getenv("DB_CLUSTER_ENDPOINT")
    if not endpoint:
        environment = os.getenv("ENV", "dev")
        region = os.getenv("AWS_REGION", "ap-northeast-1")
        endpoint = _find_cluster_endpoint(environment, region)

    return create_dsql_engine(
        cluster_endpoint=endpoint,
        db_name=os.getenv("DB_NAME", "postgres"),
        region=os.getenv("AWS_REGION", "ap-northeast-1"),
    )


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        transactional_ddl=False,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = _get_engine()

    with connectable.connect() as base_connection:
        connection = base_connection
        if base_connection.dialect.name == "postgresql":
            connection = base_connection.execution_options(isolation_level="AUTOCOMMIT")
        _run_migrations(connection)


def _run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        transactional_ddl=False,
    )

    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
