from fastapi import FastAPI
from fastapi.testclient import TestClient

from routineops.domain.exceptions import (
    AuthorizationError,
    ConflictError,
    NotFoundError,
    ValidationError,
)
from routineops.interface.api.error_handlers import register_exception_handlers


def create_test_app() -> FastAPI:
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/not-found")
    def raise_not_found() -> None:
        raise NotFoundError("Task", "123")

    @app.get("/validation")
    def raise_validation() -> None:
        raise ValidationError("bad input")

    @app.get("/conflict")
    def raise_conflict() -> None:
        raise ConflictError("already exists")

    @app.get("/auth")
    def raise_auth() -> None:
        raise AuthorizationError("forbidden")

    return app


def test_register_exception_handlers_maps_domain_errors() -> None:
    client = TestClient(create_test_app())

    not_found = client.get("/not-found")
    validation = client.get("/validation")
    conflict = client.get("/conflict")
    auth = client.get("/auth")

    assert not_found.status_code == 404
    assert not_found.json() == {"detail": "Task with id '123' not found"}

    assert validation.status_code == 422
    assert validation.json() == {"detail": "bad input"}

    assert conflict.status_code == 409
    assert conflict.json() == {"detail": "already exists"}

    assert auth.status_code == 403
    assert auth.json() == {"detail": "forbidden"}
