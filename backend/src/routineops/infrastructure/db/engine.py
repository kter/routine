"""
Aurora DSQL engine with IAM token auto-renewal via do_connect event.
Falls back to SQLite for local/test environments.
"""

import os
import logging

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine

logger = logging.getLogger(__name__)

_engine: Engine | None = None


def _get_dsql_token(hostname: str, region: str) -> str:
    """Generate an Aurora DSQL IAM authentication token."""
    import boto3

    client = boto3.client("dsql", region_name=region)
    token: str = client.generate_db_connect_admin_auth_token(
        Hostname=hostname,
        Region=region,
    )
    return token


def create_dsql_engine(
    cluster_endpoint: str,
    db_name: str,
    region: str = "ap-northeast-1",
) -> Engine:
    url = (
        f"postgresql+psycopg2://admin@{cluster_endpoint}/{db_name}"
        "?sslmode=require"
    )
    engine = create_engine(url, pool_pre_ping=True, pool_size=5, max_overflow=10)

    @event.listens_for(engine, "do_connect")
    def provide_token(dialect, conn_rec, cargs, cparams):  # type: ignore[no-untyped-def]
        token = _get_dsql_token(cluster_endpoint, region)
        cparams["password"] = token

    return engine


def create_sqlite_engine(path: str = ":memory:") -> Engine:
    return create_engine(
        f"sqlite:///{path}",
        connect_args={"check_same_thread": False},
    )


def get_engine() -> Engine:
    global _engine
    if _engine is not None:
        return _engine

    db_type = os.getenv("DB_TYPE", "dsql")

    if db_type == "sqlite":
        db_path = os.getenv("SQLITE_PATH", ":memory:")
        logger.info("Using SQLite engine at %s", db_path)
        _engine = create_sqlite_engine(db_path)
    else:
        cluster_endpoint = os.environ["DB_CLUSTER_ENDPOINT"]
        db_name = os.getenv("DB_NAME", "postgres")
        region = os.getenv("AWS_REGION", "ap-northeast-1")
        logger.info("Using Aurora DSQL engine at %s", cluster_endpoint)
        _engine = create_dsql_engine(cluster_endpoint, db_name, region)

    return _engine


def init_db() -> None:
    from routineops.infrastructure.db.base import Base
    from routineops.infrastructure.db import models as _models  # noqa: F401

    engine = get_engine()
    Base.metadata.create_all(engine)
