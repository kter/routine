from __future__ import annotations

import logging

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from routineops.domain.exceptions import (
    AuthorizationError,
    ConflictError,
    NotFoundError,
    ValidationError,
)
from routineops.infrastructure.monitoring.logging import emit_structured_log

logger = logging.getLogger(__name__)


def _detail_response(*, status_code: int, detail: str) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"detail": detail})


def _log_domain_error(
    request: Request,
    exc: Exception,
    *,
    status_code: int,
) -> None:
    emit_structured_log(
        logger,
        logging.WARNING,
        "Domain error handled",
        event_name="domain_error",
        method=request.method,
        route=request.url.path,
        status_code=status_code,
        reason=str(exc),
        outcome="error",
    )


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(NotFoundError)
    async def handle_not_found(request: Request, exc: NotFoundError) -> JSONResponse:
        _log_domain_error(request, exc, status_code=status.HTTP_404_NOT_FOUND)
        return _detail_response(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )

    @app.exception_handler(ValidationError)
    async def handle_validation(request: Request, exc: ValidationError) -> JSONResponse:
        _log_domain_error(request, exc, status_code=status.HTTP_422_UNPROCESSABLE_CONTENT)
        return _detail_response(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        )

    @app.exception_handler(ConflictError)
    async def handle_conflict(request: Request, exc: ConflictError) -> JSONResponse:
        _log_domain_error(request, exc, status_code=status.HTTP_409_CONFLICT)
        return _detail_response(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )

    @app.exception_handler(AuthorizationError)
    async def handle_authorization(request: Request, exc: AuthorizationError) -> JSONResponse:
        _log_domain_error(request, exc, status_code=status.HTTP_403_FORBIDDEN)
        return _detail_response(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        )

    @app.exception_handler(Exception)
    async def handle_unexpected(request: Request, exc: Exception) -> JSONResponse:
        logger.exception(
            "Unhandled exception raised by API request",
            extra={
                "event_name": "unexpected_exception",
                "method": request.method,
                "route": request.url.path,
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "error_type": type(exc).__name__,
                "outcome": "error",
            },
        )
        return _detail_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
