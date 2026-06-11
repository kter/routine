"""Integration tests for API authentication enforcement (no dependency overrides)."""

import pytest
from fastapi.testclient import TestClient

from routineops.config.settings import clear_settings_caches
from routineops.main import app

PROTECTED_ENDPOINTS = [
    ("GET", "/api/v1/tasks"),
    ("POST", "/api/v1/tasks"),
    ("GET", "/api/v1/executions"),
    ("POST", "/api/v1/executions"),
    ("GET", "/api/v1/dashboard"),
]


@pytest.fixture
def raw_client(monkeypatch: pytest.MonkeyPatch):
    """TestClient without auth/db overrides - real auth dependency chain.

    The root conftest enables TEST_MODE for the suite; disable it here so the
    real JWT verification path is exercised.
    """
    monkeypatch.setenv("TEST_MODE", "false")
    clear_settings_caches()
    assert not app.dependency_overrides
    with TestClient(app) as client:
        yield client
    clear_settings_caches()


class TestAuthEnforcement:
    @pytest.mark.parametrize(("method", "path"), PROTECTED_ENDPOINTS)
    def test_request_without_authorization_header_is_rejected(
        self, raw_client: TestClient, method: str, path: str
    ) -> None:
        resp = raw_client.request(method, path)

        assert resp.status_code == 401
        assert resp.json() == {"detail": "Not authenticated"}

    @pytest.mark.parametrize(("method", "path"), PROTECTED_ENDPOINTS)
    def test_request_with_invalid_bearer_token_is_rejected(
        self, raw_client: TestClient, method: str, path: str
    ) -> None:
        resp = raw_client.request(method, path, headers={"Authorization": "Bearer invalid-token"})

        assert resp.status_code == 401

    def test_request_with_non_bearer_scheme_is_rejected(self, raw_client: TestClient) -> None:
        resp = raw_client.get("/api/v1/tasks", headers={"Authorization": "Basic dXNlcjpwYXNz"})

        assert resp.status_code == 401


class TestHealthEndpoint:
    def test_health_does_not_require_authentication(self, raw_client: TestClient) -> None:
        resp = raw_client.get("/health")

        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}
