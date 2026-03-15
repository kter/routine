from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ExecutionStepResponse(BaseModel):
    id: UUID
    execution_id: UUID
    step_id: UUID
    position: int
    step_snapshot: dict[str, object]
    status: str
    evidence_text: str | None
    evidence_image_key: str | None
    evidence_image_url: str | None = None
    completed_at: datetime | None
    completed_by: str | None
    notes: str

    model_config = {"from_attributes": True}


class ExecutionResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    task_id: UUID
    task_title: str | None = None
    started_by: str
    status: str
    scheduled_for: datetime | None
    started_at: datetime
    completed_at: datetime | None
    duration_seconds: int | None
    notes: str
    steps: list[ExecutionStepResponse] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class StartExecutionRequest(BaseModel):
    task_id: UUID
    scheduled_for: datetime | None = None
    notes: str = ""


class CompleteStepRequest(BaseModel):
    evidence_text: str | None = None
    evidence_image_key: str | None = None
    notes: str = ""


class CompleteExecutionRequest(BaseModel):
    notes: str = ""


class AbandonExecutionRequest(BaseModel):
    notes: str = ""


class EvidenceUploadUrlRequest(BaseModel):
    content_type: str


class EvidenceUploadUrlResponse(BaseModel):
    upload_url: str
    key: str
