from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

from routineops.config.settings import ApiSettings, get_api_settings
from routineops.infrastructure.db.engine import init_db
from routineops.infrastructure.monitoring.sentry import init_sentry
from routineops.interface.api.v1.router import router as v1_router

init_sentry(include_fastapi=True)


def create_app(settings: ApiSettings | None = None) -> FastAPI:
    settings = settings or get_api_settings()
    app = FastAPI(
        title="RoutineOps API",
        version="1.0.0",
        docs_url="/docs" if settings.env != "prd" else None,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(v1_router, prefix="/api/v1")

    @app.on_event("startup")
    async def startup() -> None:
        init_db()

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()

# AWS Lambda handler via Mangum
handler = Mangum(app, lifespan="off")
