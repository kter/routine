from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class DashboardTaskItem(BaseModel):
    task_id: UUID
    title: str
    scheduled_for: datetime
    estimated_minutes: int
    execution_id: UUID | None
    status: str | None


class DashboardResponse(BaseModel):
    today: list[DashboardTaskItem]
    overdue: list[DashboardTaskItem]
    upcoming: list[DashboardTaskItem]
