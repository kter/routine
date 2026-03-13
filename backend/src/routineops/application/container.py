from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from routineops.infrastructure.repositories.execution_repository_impl import (
    ExecutionRepositoryImpl,
)
from routineops.infrastructure.repositories.task_repository_impl import TaskRepositoryImpl
from routineops.infrastructure.storage.s3_storage import S3StorageImpl
from routineops.usecases.dashboard_usecases import DashboardUsecases
from routineops.usecases.execution_usecases import ExecutionUsecases
from routineops.usecases.task_usecases import TaskUsecases


def build_task_repository(*, db: Session, tenant_id: UUID) -> TaskRepositoryImpl:
    return TaskRepositoryImpl(db, tenant_id)


def build_execution_repository(*, db: Session, tenant_id: UUID) -> ExecutionRepositoryImpl:
    return ExecutionRepositoryImpl(db, tenant_id)


def build_storage(*, bucket_name: str | None = None) -> S3StorageImpl:
    return S3StorageImpl(bucket_name=bucket_name)


def build_task_usecases(*, db: Session, tenant_id: UUID) -> TaskUsecases:
    task_repo = build_task_repository(db=db, tenant_id=tenant_id)
    return TaskUsecases(task_repo)


def build_execution_usecases(
    *,
    db: Session,
    tenant_id: UUID,
    storage: S3StorageImpl,
) -> ExecutionUsecases:
    exec_repo = build_execution_repository(db=db, tenant_id=tenant_id)
    task_repo = build_task_repository(db=db, tenant_id=tenant_id)
    return ExecutionUsecases(exec_repo, task_repo, storage)


def build_dashboard_usecases(*, db: Session, tenant_id: UUID) -> DashboardUsecases:
    task_repo = build_task_repository(db=db, tenant_id=tenant_id)
    exec_repo = build_execution_repository(db=db, tenant_id=tenant_id)
    return DashboardUsecases(task_repo, exec_repo)
