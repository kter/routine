"""
Aurora DSQL engine with IAM token auto-renewal via do_connect event.
Falls back to SQLite for local/test environments.
"""

import logging

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine

from routineops.config.settings import DatabaseSettings, get_database_settings

logger = logging.getLogger(__name__)

_engine: Engine | None = None


def reset_engine() -> None:
    global _engine
    if _engine is not None and hasattr(_engine, "dispose"):
        _engine.dispose()
    _engine = None


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
    url = f"postgresql+psycopg2://admin@{cluster_endpoint}/{db_name}?sslmode=require"
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


def get_engine(settings: DatabaseSettings | None = None) -> Engine:
    global _engine
    if _engine is not None:
        return _engine

    settings = settings or get_database_settings()
    db_type = settings.db_type

    if db_type == "sqlite":
        logger.info("Using SQLite engine at %s", settings.sqlite_path)
        _engine = create_sqlite_engine(settings.sqlite_path)
    else:
        if not settings.db_cluster_endpoint:
            raise ValueError("DB_CLUSTER_ENDPOINT is required when DB_TYPE is not sqlite")
        logger.info("Using Aurora DSQL engine at %s", settings.db_cluster_endpoint)
        _engine = create_dsql_engine(
            settings.db_cluster_endpoint,
            settings.db_name,
            settings.aws_region,
        )

    return _engine


def init_db(settings: DatabaseSettings | None = None) -> None:
    settings = settings or get_database_settings()
    if settings.db_type != "sqlite":
        logger.info("Skipping create_all for non-SQLite DB; use Alembic migrations instead")
        return

    from routineops.infrastructure.db import models as _models  # noqa: F401
    from routineops.infrastructure.db.base import Base

    engine = get_engine(settings)
    Base.metadata.create_all(engine)
