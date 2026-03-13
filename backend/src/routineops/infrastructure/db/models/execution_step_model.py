from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from routineops.infrastructure.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from routineops.infrastructure.db.models.execution_model import ExecutionModel


class ExecutionStepModel(Base, TimestampMixin):
    __tablename__ = "execution_steps"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    execution_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("executions.id"), nullable=False
    )
    step_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    step_snapshot: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False, default="pending")
    evidence_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    evidence_image_key: Mapped[str | None] = mapped_column(Text, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_by: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str] = mapped_column(Text, nullable=False, default="")

    execution: Mapped["ExecutionModel"] = relationship("ExecutionModel", back_populates="steps")
