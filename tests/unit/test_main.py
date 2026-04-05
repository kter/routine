from unittest.mock import patch

from fastapi.testclient import TestClient

from routineops.config.settings import ApiSettings
from routineops.main import create_app


def test_create_app_uses_settings_for_docs_and_cors() -> None:
    settings = ApiSettings.model_validate(
        {
            "ENV": "prd",
            "CORS_ORIGINS": "https://app.example.com,https://admin.example.com",
        }
    )

    app = create_app(settings)

    assert app.docs_url is None
    cors = next(
        middleware
        for middleware in app.user_middleware
        if middleware.cls.__name__ == "CORSMiddleware"
    )
    assert cors.kwargs["allow_origins"] == [
        "https://app.example.com",
        "https://admin.example.com",
    ]


def test_create_app_echoes_request_id_and_logs_completion() -> None:
    settings = ApiSettings.model_validate(
        {
            "ENV": "dev",
            "LOG_FORMAT": "plain",
        }
    )
    app = create_app(settings)

    with patch("routineops.main.emit_structured_log") as emit_structured_log:
        with TestClient(app) as client:
            response = client.get("/health", headers={"X-Request-ID": "req-123"})

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "req-123"

    completion_log = next(
        call
        for call in emit_structured_log.call_args_list
        if call.kwargs.get("event_name") == "http_request_completed"
    )
    assert completion_log.kwargs["status_code"] == 200
    assert completion_log.kwargs["method"] == "GET"
    assert completion_log.kwargs["route"] == "/health"
