import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

from routineops.infrastructure.db.engine import init_db
from routineops.interface.api.v1.router import router as v1_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="RoutineOps API",
        version="1.0.0",
        docs_url="/docs" if os.getenv("ENV") != "prd" else None,
    )

    cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
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
