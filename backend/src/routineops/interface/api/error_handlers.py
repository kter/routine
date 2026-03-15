from __future__ import annotations

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from routineops.domain.exceptions import (
    AuthorizationError,
    ConflictError,
    NotFoundError,
    ValidationError,
)


def _detail_response(*, status_code: int, detail: str) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"detail": detail})


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(NotFoundError)
    async def handle_not_found(_: Request, exc: NotFoundError) -> JSONResponse:
        return _detail_response(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )

    @app.exception_handler(ValidationError)
    async def handle_validation(_: Request, exc: ValidationError) -> JSONResponse:
        return _detail_response(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        )

    @app.exception_handler(ConflictError)
    async def handle_conflict(_: Request, exc: ConflictError) -> JSONResponse:
        return _detail_response(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )

    @app.exception_handler(AuthorizationError)
    async def handle_authorization(_: Request, exc: AuthorizationError) -> JSONResponse:
        return _detail_response(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        )
