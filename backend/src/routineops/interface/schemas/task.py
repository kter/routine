from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class StepResponse(BaseModel):
    id: UUID
    task_id: UUID
    position: int
    title: str
    instruction: str
    evidence_type: str
    is_required: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TaskResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    title: str
    description: str
    cron_expression: str
    timezone: str
    estimated_minutes: int
    is_active: bool
    tags: list[str]
    created_by: str
    created_at: datetime
    updated_at: datetime
    steps: list[StepResponse] = []

    model_config = {"from_attributes": True}


class CreateStepRequest(BaseModel):
    position: int = Field(ge=1)
    title: str = Field(min_length=1)
    instruction: str = ""
    evidence_type: str = "none"
    is_required: bool = True


class CreateTaskRequest(BaseModel):
    title: str = Field(min_length=1)
    description: str = ""
    cron_expression: str = Field(min_length=1)
    timezone: str = "Asia/Tokyo"
    estimated_minutes: int = Field(default=30, ge=1)
    tags: list[str] = []
    steps: list[CreateStepRequest] = []


class UpdateTaskRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    cron_expression: str | None = None
    timezone: str | None = None
    estimated_minutes: int | None = Field(default=None, ge=1)
    is_active: bool | None = None
    tags: list[str] | None = None
