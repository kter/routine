from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, Integer, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from routineops.infrastructure.db.base import Base, TimestampMixin
from routineops.infrastructure.db.dsql_compat import JsonObjectText

if TYPE_CHECKING:
    from routineops.infrastructure.db.models.execution_step_model import ExecutionStepModel


class ExecutionModel(Base, TimestampMixin):
    __tablename__ = "executions"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    task_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    started_by: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False, default="in_progress")
    scheduled_for: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    notes: Mapped[str] = mapped_column(Text, nullable=False, default="")
    metadata_: Mapped[dict[str, object]] = mapped_column(
        "metadata", JsonObjectText(), nullable=False, default=dict
    )

    steps: Mapped[list["ExecutionStepModel"]] = relationship(
        "ExecutionStepModel",
        back_populates="execution",
        primaryjoin="ExecutionModel.id == foreign(ExecutionStepModel.execution_id)",
        order_by="ExecutionStepModel.position",
        cascade="all, delete-orphan",
    )
