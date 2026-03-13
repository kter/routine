"""Integration test fixtures: TestClient + SQLite in-memory DB."""

from collections.abc import Generator
from contextlib import contextmanager
from unittest.mock import MagicMock
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from routineops.app.request_context import RequestContext
from routineops.infrastructure.db import (
    models as _models,  # noqa: F401 - triggers SQLAlchemy model registration
)
from routineops.infrastructure.db.base import Base
from routineops.infrastructure.db.session import get_db
from routineops.infrastructure.storage.s3_storage import S3StorageImpl
from routineops.interface.api.deps import get_current_tenant, get_storage
from routineops.main import app

TEST_TENANT_ID = UUID("00000000-0000-0000-0000-000000000001")
TEST_USER_SUB = "integration-test-user"
ALT_TEST_TENANT_ID = UUID("00000000-0000-0000-0000-000000000002")
ALT_TEST_USER_SUB = "integration-test-user-alt"


@pytest.fixture(scope="function")
def db_engine():
    """Create a fresh SQLite in-memory engine for each test."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(db_engine) -> Generator[Session, None, None]:
    factory = sessionmaker(bind=db_engine, autocommit=False, autoflush=False)
    session = factory()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def mock_storage() -> MagicMock:
    storage = MagicMock(spec=S3StorageImpl)
    storage.generate_upload_url.return_value = "https://s3.example.com/presigned-url"
    storage.generate_download_url.return_value = "https://s3.example.com/download-url"
    return storage


@pytest.fixture(scope="function")
def tenant_client_factory(
    db_session: Session,
    mock_storage: MagicMock,
) -> Generator:
    """Build TestClient instances bound to a specific tenant."""

    @contextmanager
    def factory(
        tenant_id: UUID = TEST_TENANT_ID,
        user_sub: str = TEST_USER_SUB,
    ) -> Generator[TestClient, None, None]:
        def override_get_db():
            yield db_session

        def override_get_tenant():
            return RequestContext(tenant_id=tenant_id, user_sub=user_sub)

        def override_get_storage():
            return mock_storage

        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_current_tenant] = override_get_tenant
        app.dependency_overrides[get_storage] = override_get_storage

        with TestClient(app) as client:
            yield client

        app.dependency_overrides.clear()

    try:
        yield factory
    finally:
        app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def client(tenant_client_factory) -> Generator[TestClient, None, None]:
    """Default TestClient bound to the primary test tenant."""

    with tenant_client_factory() as default_client:
        yield default_client
