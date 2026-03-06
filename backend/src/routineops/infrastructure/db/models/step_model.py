from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, Integer, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from routineops.infrastructure.db.base import Base, TimestampMixin


class StepModel(Base, TimestampMixin):
    __tablename__ = "steps"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    task_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("tasks.id"), nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    instruction: Mapped[str] = mapped_column(Text, nullable=False, default="")
    evidence_type: Mapped[str] = mapped_column(Text, nullable=False, default="none")
    is_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    task: Mapped["TaskModel"] = relationship("TaskModel", back_populates="steps")


from routineops.infrastructure.db.models.task_model import TaskModel  # noqa: E402, F401
