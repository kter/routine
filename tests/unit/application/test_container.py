from unittest.mock import MagicMock
from uuid import UUID

from sqlalchemy.orm import Session

from routineops.application.container import (
    build_dashboard_usecases,
    build_execution_usecases,
    build_storage,
    build_task_usecases,
)
from routineops.infrastructure.storage.s3_storage import S3StorageImpl
from routineops.usecases.dashboard_usecases import DashboardUsecases
from routineops.usecases.execution_usecases import ExecutionUsecases
from routineops.usecases.task_usecases import TaskUsecases


def test_build_task_usecases_returns_task_usecases() -> None:
    db_session = MagicMock(spec=Session)
    usecases = build_task_usecases(
        db=db_session,
        tenant_id=UUID("00000000-0000-0000-0000-000000000001"),
    )

    assert isinstance(usecases, TaskUsecases)


def test_build_execution_usecases_uses_injected_storage() -> None:
    db_session = MagicMock(spec=Session)
    storage = build_storage(bucket_name="test-bucket")

    usecases = build_execution_usecases(
        db=db_session,
        tenant_id=UUID("00000000-0000-0000-0000-000000000001"),
        storage=storage,
    )

    assert isinstance(usecases, ExecutionUsecases)
    assert usecases._storage is storage


def test_build_dashboard_usecases_returns_dashboard_usecases() -> None:
    db_session = MagicMock(spec=Session)
    usecases = build_dashboard_usecases(
        db=db_session,
        tenant_id=UUID("00000000-0000-0000-0000-000000000001"),
    )

    assert isinstance(usecases, DashboardUsecases)


def test_build_storage_returns_storage_adapter() -> None:
    storage = build_storage(bucket_name="test-bucket")

    assert isinstance(storage, S3StorageImpl)
