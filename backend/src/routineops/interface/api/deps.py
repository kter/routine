"""FastAPI dependency injection utilities."""

import os
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from routineops.infrastructure.db.session import get_db
from routineops.infrastructure.repositories.execution_repository_impl import (
    ExecutionRepositoryImpl,
)
from routineops.infrastructure.repositories.task_repository_impl import (
    TaskRepositoryImpl,
)
from routineops.infrastructure.storage.s3_storage import S3StorageImpl
from routineops.usecases.dashboard_usecases import DashboardUsecases
from routineops.usecases.execution_usecases import ExecutionUsecases
from routineops.usecases.task_usecases import TaskUsecases

security = HTTPBearer()


def get_current_tenant(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> tuple[UUID, str]:
    """
    Verify JWT and extract (tenant_id, user_sub).
    Returns (tenant_id, sub) tuple.
    """
    token = credentials.credentials

    # Allow bypass in test mode
    if os.getenv("TEST_MODE") == "true":
        tenant_id = UUID(os.getenv("TEST_TENANT_ID", "00000000-0000-0000-0000-000000000001"))
        sub = os.getenv("TEST_USER_SUB", "test-user")
        return tenant_id, sub

    try:
        from routineops.infrastructure.auth.cognito import verify_token

        claims = verify_token(token)
        sub = str(claims.get("sub", ""))
        tenant_id_str = str(claims.get("custom:tenant_id", ""))
        if not tenant_id_str:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="tenant_id not found in token",
            )
        return UUID(tenant_id_str), sub
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        ) from e


TenantDep = Annotated[tuple[UUID, str], Depends(get_current_tenant)]
DbDep = Annotated[Session, Depends(get_db)]


def get_task_repo(tenant: TenantDep, db: DbDep) -> TaskRepositoryImpl:
    tenant_id, _ = tenant
    return TaskRepositoryImpl(db, tenant_id)


def get_exec_repo(tenant: TenantDep, db: DbDep) -> ExecutionRepositoryImpl:
    tenant_id, _ = tenant
    return ExecutionRepositoryImpl(db, tenant_id)


def get_storage() -> S3StorageImpl:
    return S3StorageImpl()


def get_task_usecases(
    task_repo: Annotated[TaskRepositoryImpl, Depends(get_task_repo)],
) -> TaskUsecases:
    return TaskUsecases(task_repo)


def get_execution_usecases(
    exec_repo: Annotated[ExecutionRepositoryImpl, Depends(get_exec_repo)],
    task_repo: Annotated[TaskRepositoryImpl, Depends(get_task_repo)],
    storage: Annotated[S3StorageImpl, Depends(get_storage)],
) -> ExecutionUsecases:
    return ExecutionUsecases(exec_repo, task_repo, storage)


def get_dashboard_usecases(
    task_repo: Annotated[TaskRepositoryImpl, Depends(get_task_repo)],
    exec_repo: Annotated[ExecutionRepositoryImpl, Depends(get_exec_repo)],
) -> DashboardUsecases:
    return DashboardUsecases(task_repo, exec_repo)
