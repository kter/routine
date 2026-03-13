import os
from unittest.mock import patch

from routineops.config.settings import (
    clear_settings_caches,
    get_api_settings,
    get_post_confirmation_settings,
)


def test_get_api_settings_reads_env_overrides() -> None:
    with patch.dict(
        os.environ,
        {
            "ENV": "prd",
            "CORS_ORIGINS": "https://app.example.com, https://admin.example.com ",
            "TEST_MODE": "true",
            "TEST_TENANT_ID": "00000000-0000-0000-0000-000000000123",
            "TEST_USER_SUB": "settings-user",
        },
        clear=False,
    ):
        clear_settings_caches()
        settings = get_api_settings()

    assert settings.env == "prd"
    assert settings.test_mode is True
    assert str(settings.test_tenant_id) == "00000000-0000-0000-0000-000000000123"
    assert settings.test_user_sub == "settings-user"
    assert settings.cors_origins_list == [
        "https://app.example.com",
        "https://admin.example.com",
    ]


def test_get_post_confirmation_settings_uses_defaults() -> None:
    with patch.dict(os.environ, {}, clear=False):
        clear_settings_caches()
        settings = get_post_confirmation_settings()

    assert settings.aws_region == "ap-northeast-1"
    assert settings.db_name == "postgres"
