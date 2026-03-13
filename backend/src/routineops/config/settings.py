from __future__ import annotations

from functools import lru_cache
from uuid import UUID

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    aws_region: str = Field(default="ap-northeast-1", alias="AWS_REGION")
    db_type: str = Field(default="dsql", alias="DB_TYPE")
    sqlite_path: str = Field(default=":memory:", alias="SQLITE_PATH")
    db_cluster_endpoint: str | None = Field(default=None, alias="DB_CLUSTER_ENDPOINT")
    db_name: str = Field(default="postgres", alias="DB_NAME")


class ApiSettings(DatabaseSettings):
    env: str = Field(default="development", alias="ENV")
    cors_origins: str = Field(default="http://localhost:5173", alias="CORS_ORIGINS")
    test_mode: bool = Field(default=False, alias="TEST_MODE")
    test_tenant_id: UUID = Field(
        default=UUID("00000000-0000-0000-0000-000000000001"),
        alias="TEST_TENANT_ID",
    )
    test_user_sub: str = Field(default="test-user", alias="TEST_USER_SUB")
    cognito_client_id: str | None = Field(default=None, alias="COGNITO_CLIENT_ID")
    cognito_jwks_url: str | None = Field(default=None, alias="COGNITO_JWKS_URL")
    evidence_bucket_name: str | None = Field(default=None, alias="EVIDENCE_BUCKET_NAME")

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


class PostConfirmationSettings(DatabaseSettings):
    env: str = Field(default="development", alias="ENV")


@lru_cache(maxsize=1)
def get_database_settings() -> DatabaseSettings:
    return DatabaseSettings()


@lru_cache(maxsize=1)
def get_api_settings() -> ApiSettings:
    return ApiSettings()


@lru_cache(maxsize=1)
def get_post_confirmation_settings() -> PostConfirmationSettings:
    return PostConfirmationSettings()


def clear_settings_caches() -> None:
    get_database_settings.cache_clear()
    get_api_settings.cache_clear()
    get_post_confirmation_settings.cache_clear()
