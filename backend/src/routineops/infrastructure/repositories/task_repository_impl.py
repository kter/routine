from __future__ import annotations

import json
from uuid import UUID

from sqlalchemy.orm import Session

from routineops.domain.entities.task import Step, Task
from routineops.domain.value_objects.cron_expression import CronExpression
from routineops.domain.value_objects.evidence_type import EvidenceType
from routineops.infrastructure.db.models.step_model import StepModel
from routineops.infrastructure.db.models.task_model import TaskModel
from routineops.infrastructure.repositories.base_repository import BaseRepository
from routineops.usecases.interfaces.task_repository import TaskRepositoryPort


class TaskRepositoryImpl(BaseRepository, TaskRepositoryPort):
    def __init__(self, db: Session, tenant_id: UUID) -> None:
        super().__init__(db, tenant_id)

    def list(self, tenant_id: UUID, active_only: bool = False) -> list[Task]:
        q = self._db.query(TaskModel).filter(TaskModel.tenant_id == tenant_id)
        if active_only:
            q = q.filter(TaskModel.is_active.is_(True))
        return [self._to_domain(m) for m in q.order_by(TaskModel.created_at.desc()).all()]

    def get(self, tenant_id: UUID, task_id: UUID) -> Task | None:
        m = (
            self._db.query(TaskModel)
            .filter(TaskModel.tenant_id == tenant_id, TaskModel.id == task_id)
            .first()
        )
        return self._to_domain(m) if m else None

    def get_with_steps(self, tenant_id: UUID, task_id: UUID) -> Task | None:
        from sqlalchemy.orm import joinedload

        m = (
            self._db.query(TaskModel)
            .options(joinedload(TaskModel.steps))
            .filter(TaskModel.tenant_id == tenant_id, TaskModel.id == task_id)
            .first()
        )
        if m is None:
            return None
        task = self._to_domain(m)
        task.steps = [self._step_to_domain(s) for s in m.steps]
        return task

    def create(self, task: Task) -> Task:
        m = self._task_to_model(task)
        m.steps = [self._step_to_model(step) for step in task.steps]
        self._db.add(m)
        self._db.commit()
        created_task = self.get_with_steps(task.tenant_id, task.id)
        if created_task is None:
            raise ValueError(f"Task {task.id} not found")
        return created_task

    def update(self, task: Task) -> Task:
        from sqlalchemy.orm import joinedload

        m = (
            self._db.query(TaskModel)
            .options(joinedload(TaskModel.steps))
            .filter(TaskModel.id == task.id, TaskModel.tenant_id == task.tenant_id)
            .first()
        )
        if m is None:
            raise ValueError(f"Task {task.id} not found")
        self._apply_task_fields(m, task)
        m.steps = [self._step_to_model(step) for step in task.steps]
        self._db.commit()
        updated_task = self.get_with_steps(task.tenant_id, task.id)
        if updated_task is None:
            raise ValueError(f"Task {task.id} not found")
        return updated_task

    def delete(self, tenant_id: UUID, task_id: UUID) -> None:
        m = (
            self._db.query(TaskModel)
            .filter(TaskModel.tenant_id == tenant_id, TaskModel.id == task_id)
            .first()
        )
        if m:
            self._db.delete(m)
            self._db.commit()

    @staticmethod
    def _task_to_model(task: Task) -> TaskModel:
        return TaskModel(
            id=task.id,
            tenant_id=task.tenant_id,
            title=task.title,
            description=task.description,
            cron_expression=str(task.cron_expression),
            timezone=task.timezone,
            estimated_minutes=task.estimated_minutes,
            is_active=task.is_active,
            tags=task.tags,
            metadata_=task.metadata,
            created_by=task.created_by,
            created_at=task.created_at,
            updated_at=task.updated_at,
        )

    @staticmethod
    def _apply_task_fields(model: TaskModel, task: Task) -> None:
        model.title = task.title
        model.description = task.description
        model.cron_expression = str(task.cron_expression)
        model.timezone = task.timezone
        model.estimated_minutes = task.estimated_minutes
        model.is_active = task.is_active
        model.tags = task.tags
        model.metadata_ = task.metadata
        model.updated_at = task.updated_at

    @staticmethod
    def _step_to_model(step: Step) -> StepModel:
        return StepModel(
            id=step.id,
            tenant_id=step.tenant_id,
            task_id=step.task_id,
            position=step.position,
            title=step.title,
            instruction=step.instruction,
            evidence_type=step.evidence_type.value,
            is_required=step.is_required,
            created_at=step.created_at,
            updated_at=step.updated_at,
        )

    @staticmethod
    def _to_domain(m: TaskModel) -> Task:
        tags = m.tags
        if isinstance(tags, str):
            tags = json.loads(tags)
        metadata = m.metadata_
        if isinstance(metadata, str):
            metadata = json.loads(metadata)
        return Task(
            id=m.id,
            tenant_id=m.tenant_id,
            title=m.title,
            description=m.description,
            cron_expression=CronExpression(m.cron_expression),
            timezone=m.timezone,
            estimated_minutes=m.estimated_minutes,
            is_active=m.is_active,
            tags=list(tags or []),
            metadata=dict(metadata or {}),
            created_by=m.created_by,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )

    @staticmethod
    def _step_to_domain(m: StepModel) -> Step:
        return Step(
            id=m.id,
            tenant_id=m.tenant_id,
            task_id=m.task_id,
            position=m.position,
            title=m.title,
            instruction=m.instruction,
            evidence_type=EvidenceType(m.evidence_type),
            is_required=m.is_required,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )
