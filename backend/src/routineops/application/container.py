from __future__ import annotations

from sqlalchemy.orm import Session

from routineops.app.request_context import RequestContext
from routineops.application.dashboard import DashboardService
from routineops.application.executions import ExecutionService
from routineops.application.tasks import TaskService
from routineops.infrastructure.repositories.execution_repository_impl import (
    ExecutionRepositoryImpl,
)
from routineops.infrastructure.repositories.task_repository_impl import TaskRepositoryImpl
from routineops.infrastructure.storage.s3_storage import S3StorageImpl


def build_task_repository(*, db: Session, context: RequestContext) -> TaskRepositoryImpl:
    return TaskRepositoryImpl(db, context.tenant_id)


def build_execution_repository(*, db: Session, context: RequestContext) -> ExecutionRepositoryImpl:
    return ExecutionRepositoryImpl(db, context.tenant_id)


def build_storage(*, bucket_name: str | None = None) -> S3StorageImpl:
    return S3StorageImpl(bucket_name=bucket_name)


def build_task_usecases(*, db: Session, context: RequestContext) -> TaskService:
    task_repo = build_task_repository(db=db, context=context)
    return TaskService(task_repo, context)


def build_execution_usecases(
    *,
    db: Session,
    context: RequestContext,
    storage: S3StorageImpl,
) -> ExecutionService:
    exec_repo = build_execution_repository(db=db, context=context)
    task_repo = build_task_repository(db=db, context=context)
    return ExecutionService(exec_repo, task_repo, storage, context)


def build_dashboard_usecases(*, db: Session, context: RequestContext) -> DashboardService:
    task_repo = build_task_repository(db=db, context=context)
    exec_repo = build_execution_repository(db=db, context=context)
    return DashboardService(task_repo, exec_repo)
