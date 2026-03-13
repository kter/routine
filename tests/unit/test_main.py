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
