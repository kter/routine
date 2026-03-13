"""FastAPI dependency injection utilities."""

from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from routineops.application.container import (
    build_dashboard_usecases,
    build_execution_usecases,
    build_storage,
    build_task_usecases,
)
from routineops.config.settings import get_api_settings
from routineops.infrastructure.db.session import get_db
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
    settings = get_api_settings()

    # Allow bypass in test mode
    if settings.test_mode:
        return settings.test_tenant_id, settings.test_user_sub

    token = credentials.credentials

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


def get_storage() -> S3StorageImpl:
    settings = get_api_settings()
    return build_storage(bucket_name=settings.evidence_bucket_name)


def get_task_usecases(tenant: TenantDep, db: DbDep) -> TaskUsecases:
    tenant_id, _ = tenant
    return build_task_usecases(db=db, tenant_id=tenant_id)


def get_execution_usecases(
    tenant: TenantDep,
    db: DbDep,
    storage: Annotated[S3StorageImpl, Depends(get_storage)],
) -> ExecutionUsecases:
    tenant_id, _ = tenant
    return build_execution_usecases(db=db, tenant_id=tenant_id, storage=storage)


def get_dashboard_usecases(tenant: TenantDep, db: DbDep) -> DashboardUsecases:
    tenant_id, _ = tenant
    return build_dashboard_usecases(db=db, tenant_id=tenant_id)
