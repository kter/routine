"""Base repository that enforces tenant_id scoping on all queries."""

from typing import Any
from uuid import UUID

from sqlalchemy.orm import Query, Session


class BaseRepository:
    def __init__(self, db: Session, tenant_id: UUID) -> None:
        self._db = db
        self._tenant_id = tenant_id

    def _assert_tenant(self, tenant_id: UUID) -> None:
        if tenant_id != self._tenant_id:
            raise ValueError(
                f"Repository tenant mismatch: expected {self._tenant_id}, got {tenant_id}"
            )

    def _query(self, model_class: type[Any]) -> Query:
        """Build a tenant-scoped query for the given SQLAlchemy model."""
        return self._db.query(model_class).filter(model_class.tenant_id == self._tenant_id)
