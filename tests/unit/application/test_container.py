from unittest.mock import MagicMock
from uuid import UUID

from sqlalchemy.orm import Session

from routineops.app.request_context import RequestContext
from routineops.application.container import (
    build_dashboard_usecases,
    build_execution_usecases,
    build_storage,
    build_task_usecases,
)
from routineops.application.dashboard import DashboardService
from routineops.application.executions import ExecutionService
from routineops.application.tasks import TaskService
from routineops.infrastructure.storage.s3_storage import S3StorageImpl


def make_context() -> RequestContext:
    return RequestContext(
        tenant_id=UUID("00000000-0000-0000-0000-000000000001"),
        user_sub="container-user",
    )


def test_build_task_usecases_returns_task_service() -> None:
    db_session = MagicMock(spec=Session)
    usecases = build_task_usecases(
        db=db_session,
        context=make_context(),
    )

    assert isinstance(usecases, TaskService)


def test_build_execution_usecases_uses_injected_storage() -> None:
    db_session = MagicMock(spec=Session)
    storage = build_storage(bucket_name="test-bucket")

    usecases = build_execution_usecases(
        db=db_session,
        context=make_context(),
        storage=storage,
    )

    assert isinstance(usecases, ExecutionService)
    assert usecases._storage is storage


def test_build_dashboard_usecases_returns_dashboard_service() -> None:
    db_session = MagicMock(spec=Session)
    usecases = build_dashboard_usecases(
        db=db_session,
        context=make_context(),
    )

    assert isinstance(usecases, DashboardService)


def test_build_storage_returns_storage_adapter() -> None:
    storage = build_storage(bucket_name="test-bucket")

    assert isinstance(storage, S3StorageImpl)
