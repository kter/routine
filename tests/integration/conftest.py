"""Integration test fixtures: TestClient + SQLite in-memory DB."""

import os
from collections.abc import Generator
from unittest.mock import MagicMock
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from routineops.infrastructure.db.base import Base
from routineops.infrastructure.db.session import get_db
from routineops.infrastructure.db import models as _models  # noqa: F401 - triggers SQLAlchemy model registration
from routineops.infrastructure.storage.s3_storage import S3StorageImpl
from routineops.interface.api.deps import get_current_tenant, get_storage
from routineops.main import app

TEST_TENANT_ID = UUID("00000000-0000-0000-0000-000000000001")
TEST_USER_SUB = "integration-test-user"


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
def client(db_session: Session, mock_storage) -> Generator[TestClient, None, None]:
    """TestClient with overridden dependencies."""

    def override_get_db():
        yield db_session

    def override_get_tenant():
        return TEST_TENANT_ID, TEST_USER_SUB

    def override_get_storage():
        return mock_storage

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_tenant] = override_get_tenant
    app.dependency_overrides[get_storage] = override_get_storage

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
