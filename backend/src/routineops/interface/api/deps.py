"""FastAPI dependency injection utilities."""

import logging
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from routineops.app.auth import TENANT_ID_CLAIM
from routineops.app.request_context import RequestContext, new_request_id
from routineops.application.container import (
    build_dashboard_service,
    build_execution_service,
    build_storage,
    build_task_service,
)
from routineops.application.dashboard import DashboardService
from routineops.application.executions import ExecutionService
from routineops.application.tasks import TaskService
from routineops.config.settings import get_api_settings
from routineops.infrastructure.db.session import get_db
from routineops.infrastructure.monitoring.logging import (
    bind_log_context,
    emit_structured_log,
    set_sentry_request_context,
)
from routineops.infrastructure.storage.s3_storage import S3StorageImpl

security = HTTPBearer()
logger = logging.getLogger(__name__)


def get_request_context(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    request: Request,
) -> RequestContext:
    """
    Verify JWT and extract request-scoped auth context.
    """
    settings = get_api_settings()

    # Allow bypass in test mode
    if settings.test_mode:
        request_id = getattr(request.state, "request_id", None)
        context = RequestContext(
            tenant_id=settings.test_tenant_id,
            user_sub=settings.test_user_sub,
            request_id=request_id or new_request_id(),
        )
        request.state.request_context = context
        bind_log_context(tenant_id=str(context.tenant_id), user_sub=context.user_sub)
        set_sentry_request_context(
            request_id=context.request_id,
            tenant_id=context.tenant_id,
            user_sub=context.user_sub,
            component="api",
        )
        emit_structured_log(
            logger,
            logging.INFO,
            "Authentication bypassed in test mode",
            event_name="auth_decision",
            decision="test_mode_bypass",
            outcome="success",
        )
        return context

    token = credentials.credentials

    try:
        from routineops.infrastructure.auth.cognito import verify_token

        claims = verify_token(token)
        sub = str(claims.get("sub", ""))
        tenant_id_str = str(claims.get(TENANT_ID_CLAIM, ""))
        if not tenant_id_str:
            emit_structured_log(
                logger,
                logging.WARNING,
                "Authentication denied due to missing tenant claim",
                event_name="auth_decision",
                decision="tenant_claim_missing",
                outcome="denied",
                reason="tenant_id not found in token",
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="tenant_id not found in token",
            )
        request_id = getattr(request.state, "request_id", None)
        context = RequestContext(
            tenant_id=UUID(tenant_id_str),
            user_sub=sub,
            auth_claims=claims,
            request_id=request_id or new_request_id(),
        )
        request.state.request_context = context
        bind_log_context(tenant_id=str(context.tenant_id), user_sub=context.user_sub)
        set_sentry_request_context(
            request_id=context.request_id,
            tenant_id=context.tenant_id,
            user_sub=context.user_sub,
            component="api",
        )
        emit_structured_log(
            logger,
            logging.INFO,
            "Authentication accepted",
            event_name="auth_decision",
            decision="jwt_verified",
            outcome="success",
        )
        return context
    except ValueError as e:
        emit_structured_log(
            logger,
            logging.WARNING,
            "Authentication denied",
            event_name="auth_decision",
            decision="jwt_invalid",
            outcome="denied",
            reason=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        ) from e


get_current_tenant = get_request_context

RequestContextDep = Annotated[RequestContext, Depends(get_request_context)]
DbDep = Annotated[Session, Depends(get_db)]


def get_storage() -> S3StorageImpl:
    settings = get_api_settings()
    return build_storage(bucket_name=settings.evidence_bucket_name)


def get_task_service(context: RequestContextDep, db: DbDep) -> TaskService:
    return build_task_service(db=db, context=context)


def get_execution_service(
    context: RequestContextDep,
    db: DbDep,
    storage: Annotated[S3StorageImpl, Depends(get_storage)],
) -> ExecutionService:
    return build_execution_service(db=db, context=context, storage=storage)


def get_dashboard_service(context: RequestContextDep, db: DbDep) -> DashboardService:
    return build_dashboard_service(db=db, context=context)
