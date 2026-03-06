from uuid import UUID

from pydantic import BaseModel, Field


class CreateStepRequest(BaseModel):
    position: int = Field(ge=1)
    title: str = Field(min_length=1)
    instruction: str = ""
    evidence_type: str = "none"
    is_required: bool = True


class UpdateStepRequest(BaseModel):
    position: int | None = Field(default=None, ge=1)
    title: str | None = None
    instruction: str | None = None
    evidence_type: str | None = None
    is_required: bool | None = None
