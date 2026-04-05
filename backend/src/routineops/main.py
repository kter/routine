import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

from routineops.config.settings import ApiSettings, get_api_settings
from routineops.infrastructure.db.engine import init_db
from routineops.infrastructure.monitoring.logging import (
    bind_log_context,
    clear_sentry_request_context,
    configure_logging,
    emit_structured_log,
    reset_log_context,
    set_sentry_request_context,
)
from routineops.infrastructure.monitoring.sentry import init_sentry
from routineops.interface.api.error_handlers import register_exception_handlers
from routineops.interface.api.v1.router import router as v1_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    init_db()
    emit_structured_log(
        logger,
        logging.INFO,
        "API application started",
        event_name="application_lifecycle",
        action="startup",
        outcome="success",
    )
    yield
    emit_structured_log(
        logger,
        logging.INFO,
        "API application stopped",
        event_name="application_lifecycle",
        action="shutdown",
        outcome="success",
    )


def create_app(settings: ApiSettings | None = None) -> FastAPI:
    settings = settings or get_api_settings()
    configure_logging(
        level=settings.log_level,
        log_format=settings.log_format,
        environment=settings.env,
        component="api",
    )
    init_sentry(include_fastapi=True)
    app = FastAPI(
        title="RoutineOps API",
        version="1.0.0",
        docs_url="/docs" if settings.env != "prd" else None,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)
    app.include_router(v1_router, prefix="/api/v1")

    @app.middleware("http")
    async def request_logging_middleware(request: Request, call_next):  # type: ignore[no-untyped-def]
        request_id = request.headers.get("X-Request-ID", "").strip() or uuid4().hex
        request.state.request_id = request_id
        context_token = bind_log_context(request_id=request_id)
        set_sentry_request_context(request_id=request_id, component="api")

        emit_structured_log(
            logger,
            logging.DEBUG,
            "HTTP request started",
            event_name="http_request_started",
            method=request.method,
            route=request.url.path,
        )

        start = perf_counter()
        response = None
        try:
            response = await call_next(request)
        finally:
            duration_ms = round((perf_counter() - start) * 1000, 3)
            route = request.scope.get("route")
            route_path = getattr(route, "path", request.url.path)
            client_ip = request.headers.get("x-forwarded-for", "").split(",")[0].strip()
            if not client_ip and request.client is not None:
                client_ip = request.client.host

            if response is not None:
                response.headers["X-Request-ID"] = request_id
                emit_structured_log(
                    logger,
                    logging.INFO,
                    "HTTP request completed",
                    event_name="http_request_completed",
                    method=request.method,
                    route=route_path,
                    status_code=response.status_code,
                    duration_ms=duration_ms,
                    client_ip=client_ip or None,
                    outcome="success" if response.status_code < 400 else "error",
                )

            clear_sentry_request_context()
            reset_log_context(context_token)
        return response

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()

# AWS Lambda handler via Mangum
handler = Mangum(app, lifespan="off")
