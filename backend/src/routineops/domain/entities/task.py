from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from routineops.domain.value_objects.cron_expression import CronExpression
from routineops.domain.value_objects.evidence_type import EvidenceType


@dataclass
class Step:
    id: UUID
    tenant_id: UUID
    task_id: UUID
    position: int
    title: str
    instruction: str
    evidence_type: EvidenceType
    is_required: bool
    created_at: datetime
    updated_at: datetime

    def to_snapshot(self) -> dict[str, str | bool]:
        return {
            "title": self.title,
            "instruction": self.instruction,
            "evidence_type": self.evidence_type.value,
            "is_required": self.is_required,
        }


@dataclass
class Task:
    id: UUID
    tenant_id: UUID
    title: str
    description: str
    cron_expression: CronExpression
    timezone: str
    estimated_minutes: int
    is_active: bool
    tags: list[str]
    metadata: dict[str, object]
    created_by: str
    created_at: datetime
    updated_at: datetime
    steps: list[Step] = field(default_factory=list)
