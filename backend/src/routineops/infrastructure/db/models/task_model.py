from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import JSON, Boolean, Integer, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from routineops.infrastructure.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from routineops.infrastructure.db.models.step_model import StepModel


class TaskModel(Base, TimestampMixin):
    __tablename__ = "tasks"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    cron_expression: Mapped[str] = mapped_column(Text, nullable=False)
    timezone: Mapped[str] = mapped_column(Text, nullable=False, default="Asia/Tokyo")
    estimated_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=30)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    tags: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    metadata_: Mapped[dict] = mapped_column("metadata", JSON, nullable=False, default=dict)
    created_by: Mapped[str] = mapped_column(Text, nullable=False)

    steps: Mapped[list["StepModel"]] = relationship(
        "StepModel",
        back_populates="task",
        order_by="StepModel.position",
        cascade="all, delete-orphan",
    )
