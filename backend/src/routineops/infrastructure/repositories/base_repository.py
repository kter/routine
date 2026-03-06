"""Base repository that enforces tenant_id scoping on all queries."""

from uuid import UUID

from sqlalchemy.orm import Session


class BaseRepository:
    def __init__(self, db: Session, tenant_id: UUID) -> None:
        self._db = db
        self._tenant_id = tenant_id

    def _tenant_filter(self, model_class: type, query: object) -> object:
        """Apply tenant_id filter to a query."""
        return query.filter(model_class.tenant_id == self._tenant_id)  # type: ignore[attr-defined]
