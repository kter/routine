from unittest.mock import patch

import pytest

from routineops.config.settings import DatabaseSettings
from routineops.infrastructure.db.engine import get_engine


def test_get_engine_uses_sqlite_settings() -> None:
    settings = DatabaseSettings.model_validate(
        {
            "DB_TYPE": "sqlite",
            "SQLITE_PATH": ":memory:",
        }
    )

    engine = get_engine(settings)

    assert str(engine.url) == "sqlite:///:memory:"


def test_get_engine_requires_cluster_endpoint_for_dsql() -> None:
    settings = DatabaseSettings.model_validate({"DB_TYPE": "dsql", "DB_CLUSTER_ENDPOINT": None})

    with pytest.raises(ValueError, match="DB_CLUSTER_ENDPOINT is required"):
        get_engine(settings)


def test_get_engine_builds_dsql_engine_from_settings() -> None:
    settings = DatabaseSettings.model_validate(
        {
            "DB_TYPE": "dsql",
            "DB_CLUSTER_ENDPOINT": "cluster.example",
            "DB_NAME": "postgres",
            "AWS_REGION": "ap-northeast-1",
        }
    )

    expected_engine = object()

    with patch(
        "routineops.infrastructure.db.engine.create_dsql_engine",
        return_value=expected_engine,
    ) as create_dsql_engine:
        engine = get_engine(settings)

    assert engine is expected_engine
    create_dsql_engine.assert_called_once_with("cluster.example", "postgres", "ap-northeast-1")
