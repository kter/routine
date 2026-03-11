from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from routineops.domain.exceptions import ValidationError
from routineops.domain.value_objects.evidence_type import EvidenceType
from routineops.domain.value_objects.execution_status import ExecutionStatus, StepStatus


@dataclass
class ExecutionStep:
    id: UUID
    tenant_id: UUID
    execution_id: UUID
    step_id: UUID
    position: int
    step_snapshot: dict[str, object]
    status: StepStatus
    evidence_text: str | None
    evidence_image_key: str | None
    completed_at: datetime | None
    completed_by: str | None
    notes: str
    created_at: datetime
    updated_at: datetime

    @property
    def evidence_type(self) -> EvidenceType:
        return EvidenceType(self.step_snapshot.get("evidence_type", "none"))

    @property
    def is_required(self) -> bool:
        return bool(self.step_snapshot.get("is_required", True))


@dataclass
class Execution:
    id: UUID
    tenant_id: UUID
    task_id: UUID
    started_by: str
    status: ExecutionStatus
    scheduled_for: datetime | None
    started_at: datetime
    completed_at: datetime | None
    duration_seconds: int | None
    notes: str
    metadata: dict[str, object]
    created_at: datetime
    updated_at: datetime
    steps: list[ExecutionStep] = field(default_factory=list)

    def can_complete(self) -> bool:
        """Check if all required steps are completed."""
        for step in self.steps:
            if step.is_required and step.status == StepStatus.PENDING:
                return False
        return True

    def validate_complete(self) -> None:
        if self.status != ExecutionStatus.IN_PROGRESS:
            raise ValidationError(f"Cannot complete execution in status '{self.status}'")
        if not self.can_complete():
            pending_required = [
                s for s in self.steps if s.is_required and s.status == StepStatus.PENDING
            ]
            raise ValidationError(f"{len(pending_required)} required step(s) are not completed")
