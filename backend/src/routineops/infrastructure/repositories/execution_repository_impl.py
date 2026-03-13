from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from routineops.domain.entities.execution import Execution, ExecutionStep
from routineops.domain.value_objects.execution_status import ExecutionStatus, StepStatus
from routineops.infrastructure.db.dsql_compat import decode_json_object
from routineops.infrastructure.db.models.execution_model import ExecutionModel
from routineops.infrastructure.db.models.execution_step_model import ExecutionStepModel
from routineops.infrastructure.repositories.base_repository import BaseRepository
from routineops.usecases.interfaces.execution_repository import ExecutionRepositoryPort


class ExecutionRepositoryImpl(BaseRepository, ExecutionRepositoryPort):
    def __init__(self, db: Session, tenant_id: UUID) -> None:
        super().__init__(db, tenant_id)

    def list(
        self,
        tenant_id: UUID,
        task_id: UUID | None = None,
        status: ExecutionStatus | None = None,
        scheduled_from: datetime | None = None,
        scheduled_to: datetime | None = None,
    ) -> list[Execution]:
        self._assert_tenant(tenant_id)
        q = self._query(ExecutionModel)
        if task_id is not None:
            q = q.filter(ExecutionModel.task_id == task_id)
        if status is not None:
            q = q.filter(ExecutionModel.status == status.value)
        if scheduled_from is not None:
            q = q.filter(ExecutionModel.scheduled_for >= scheduled_from)
        if scheduled_to is not None:
            q = q.filter(ExecutionModel.scheduled_for <= scheduled_to)
        return [self._to_domain(m) for m in q.order_by(ExecutionModel.started_at.desc()).all()]

    def get(self, tenant_id: UUID, execution_id: UUID) -> Execution | None:
        self._assert_tenant(tenant_id)
        m = self._query(ExecutionModel).filter(ExecutionModel.id == execution_id).first()
        return self._to_domain(m) if m else None

    def get_with_steps(self, tenant_id: UUID, execution_id: UUID) -> Execution | None:
        from sqlalchemy.orm import joinedload

        self._assert_tenant(tenant_id)
        m = (
            self._query(ExecutionModel)
            .options(joinedload(ExecutionModel.steps))
            .filter(ExecutionModel.id == execution_id)
            .first()
        )
        if m is None:
            return None
        execution = self._to_domain(m)
        execution.steps = [self._step_to_domain(s) for s in m.steps]
        return execution

    def create(self, execution: Execution) -> Execution:
        m = ExecutionModel(
            id=execution.id,
            tenant_id=execution.tenant_id,
            task_id=execution.task_id,
            started_by=execution.started_by,
            status=execution.status.value,
            scheduled_for=execution.scheduled_for,
            started_at=execution.started_at,
            completed_at=execution.completed_at,
            duration_seconds=execution.duration_seconds,
            notes=execution.notes,
            metadata_=execution.metadata,
            created_at=execution.created_at,
            updated_at=execution.updated_at,
        )
        self._db.add(m)
        self._db.commit()
        self._db.refresh(m)
        return self._to_domain(m)

    def update(self, execution: Execution) -> Execution:
        m = self._query(ExecutionModel).filter(ExecutionModel.id == execution.id).first()
        if m is None:
            raise ValueError(f"Execution {execution.id} not found")
        m.status = execution.status.value
        m.completed_at = execution.completed_at
        m.duration_seconds = execution.duration_seconds
        m.notes = execution.notes
        m.updated_at = execution.updated_at
        self._db.commit()
        self._db.refresh(m)
        return self._to_domain(m)

    def create_step(self, step: ExecutionStep) -> ExecutionStep:
        m = ExecutionStepModel(
            id=step.id,
            tenant_id=step.tenant_id,
            execution_id=step.execution_id,
            step_id=step.step_id,
            position=step.position,
            step_snapshot=step.step_snapshot,
            status=step.status.value,
            evidence_text=step.evidence_text,
            evidence_image_key=step.evidence_image_key,
            completed_at=step.completed_at,
            completed_by=step.completed_by,
            notes=step.notes,
            created_at=step.created_at,
            updated_at=step.updated_at,
        )
        self._db.add(m)
        self._db.commit()
        self._db.refresh(m)
        return self._step_to_domain(m)

    def update_step(self, step: ExecutionStep) -> ExecutionStep:
        m = self._query(ExecutionStepModel).filter(ExecutionStepModel.id == step.id).first()
        if m is None:
            raise ValueError(f"ExecutionStep {step.id} not found")
        m.status = step.status.value
        m.evidence_text = step.evidence_text
        m.evidence_image_key = step.evidence_image_key
        m.completed_at = step.completed_at
        m.completed_by = step.completed_by
        m.notes = step.notes
        m.updated_at = step.updated_at
        self._db.commit()
        self._db.refresh(m)
        return self._step_to_domain(m)

    @staticmethod
    def _to_domain(m: ExecutionModel) -> Execution:
        return Execution(
            id=m.id,
            tenant_id=m.tenant_id,
            task_id=m.task_id,
            started_by=m.started_by,
            status=ExecutionStatus(m.status),
            scheduled_for=m.scheduled_for,
            started_at=m.started_at,
            completed_at=m.completed_at,
            duration_seconds=m.duration_seconds,
            notes=m.notes,
            metadata=decode_json_object(m.metadata_),
            created_at=m.created_at,
            updated_at=m.updated_at,
        )

    @staticmethod
    def _step_to_domain(m: ExecutionStepModel) -> ExecutionStep:
        return ExecutionStep(
            id=m.id,
            tenant_id=m.tenant_id,
            execution_id=m.execution_id,
            step_id=m.step_id,
            position=m.position,
            step_snapshot=decode_json_object(m.step_snapshot),
            status=StepStatus(m.status),
            evidence_text=m.evidence_text,
            evidence_image_key=m.evidence_image_key,
            completed_at=m.completed_at,
            completed_by=m.completed_by,
            notes=m.notes,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )
