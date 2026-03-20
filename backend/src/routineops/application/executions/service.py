from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from routineops.app.request_context import RequestContext
from routineops.application.executions.ports import ExecutionRepositoryPort
from routineops.application.shared.ports import StoragePort
from routineops.application.tasks.ports import TaskRepositoryPort
from routineops.domain.entities.execution import Execution, ExecutionStep
from routineops.domain.exceptions import NotFoundError, ValidationError
from routineops.domain.value_objects.execution_status import ExecutionStatus, StepStatus


class ExecutionService:
    def __init__(
        self,
        exec_repo: ExecutionRepositoryPort,
        task_repo: TaskRepositoryPort,
        storage: StoragePort,
        context: RequestContext,
    ) -> None:
        self._exec_repo = exec_repo
        self._task_repo = task_repo
        self._storage = storage
        self._context = context

    def start_execution(
        self,
        task_id: UUID,
        scheduled_for: datetime | None = None,
        notes: str = "",
    ) -> Execution:
        task = self._task_repo.get_with_steps(task_id)
        if task is None:
            raise NotFoundError("Task", str(task_id))

        if not task.is_active:
            raise ValidationError(f"Task '{task.title}' is not active")

        now = datetime.now(tz=UTC)
        execution = Execution(
            id=uuid4(),
            tenant_id=self._context.tenant_id,
            task_id=task_id,
            started_by=self._context.user_sub,
            status=ExecutionStatus.IN_PROGRESS,
            scheduled_for=scheduled_for,
            started_at=now,
            completed_at=None,
            duration_seconds=None,
            notes=notes,
            metadata={},
            created_at=now,
            updated_at=now,
        )
        created_exec = self._exec_repo.create(execution)

        created_exec.steps = []
        for step in sorted(task.steps, key=lambda s: s.position):
            exec_step = ExecutionStep(
                id=uuid4(),
                tenant_id=self._context.tenant_id,
                execution_id=created_exec.id,
                step_id=step.id,
                position=step.position,
                step_snapshot=step.to_snapshot(),
                status=StepStatus.PENDING,
                evidence_text=None,
                evidence_image_key=None,
                completed_at=None,
                completed_by=None,
                notes="",
                created_at=now,
                updated_at=now,
            )
            created_step = self._exec_repo.create_step(exec_step)
            created_exec.steps.append(created_step)

        return created_exec

    def complete_step(
        self,
        execution_id: UUID,
        step_id: UUID,
        evidence_text: str | None = None,
        evidence_image_key: str | None = None,
        notes: str = "",
    ) -> ExecutionStep:
        execution = self._exec_repo.get_with_steps(execution_id)
        if execution is None:
            raise NotFoundError("Execution", str(execution_id))

        if execution.status != ExecutionStatus.IN_PROGRESS:
            raise ValidationError(f"Cannot modify execution in status '{execution.status}'")

        step = next((s for s in execution.steps if s.id == step_id), None)
        if step is None:
            raise NotFoundError("ExecutionStep", str(step_id))

        if step.status != StepStatus.PENDING:
            raise ValidationError(f"Step is already '{step.status}'")

        if step.evidence_type.value == "text" and not evidence_text:
            raise ValidationError("Evidence text is required for this step")
        if step.evidence_type.value == "image" and not evidence_image_key:
            raise ValidationError("Evidence image is required for this step")

        now = datetime.now(tz=UTC)
        step.status = StepStatus.COMPLETED
        step.evidence_text = evidence_text
        step.evidence_image_key = evidence_image_key
        step.completed_at = now
        step.completed_by = self._context.user_sub
        step.notes = notes
        step.updated_at = now

        return self._exec_repo.update_step(step)

    def skip_step(
        self,
        execution_id: UUID,
        step_id: UUID,
    ) -> ExecutionStep:
        execution = self._exec_repo.get_with_steps(execution_id)
        if execution is None:
            raise NotFoundError("Execution", str(execution_id))

        if execution.status != ExecutionStatus.IN_PROGRESS:
            raise ValidationError(f"Cannot modify execution in status '{execution.status}'")

        step = next((s for s in execution.steps if s.id == step_id), None)
        if step is None:
            raise NotFoundError("ExecutionStep", str(step_id))

        if step.status != StepStatus.PENDING:
            raise ValidationError(f"Step is already '{step.status}'")

        if step.is_required:
            raise ValidationError("Cannot skip a required step")

        step.status = StepStatus.SKIPPED
        step.updated_at = datetime.now(tz=UTC)
        return self._exec_repo.update_step(step)

    def complete_execution(
        self,
        execution_id: UUID,
        notes: str = "",
    ) -> Execution:
        execution = self._exec_repo.get_with_steps(execution_id)
        if execution is None:
            raise NotFoundError("Execution", str(execution_id))

        execution.validate_complete()

        now = datetime.now(tz=UTC)
        started_at = execution.started_at
        if started_at.tzinfo is None:
            started_at = started_at.replace(tzinfo=UTC)
        duration = int((now - started_at).total_seconds())

        execution.status = ExecutionStatus.COMPLETED
        execution.completed_at = now
        execution.duration_seconds = duration
        if notes:
            execution.notes = notes
        execution.updated_at = now

        return self._exec_repo.update(execution)

    def abandon_execution(
        self,
        execution_id: UUID,
        notes: str = "",
    ) -> Execution:
        execution = self._exec_repo.get_with_steps(execution_id)
        if execution is None:
            raise NotFoundError("Execution", str(execution_id))

        if execution.status != ExecutionStatus.IN_PROGRESS:
            raise ValidationError(f"Cannot abandon execution in status '{execution.status}'")

        now = datetime.now(tz=UTC)
        execution.status = ExecutionStatus.ABANDONED
        execution.completed_at = now
        if notes:
            execution.notes = notes
        execution.updated_at = now

        return self._exec_repo.update(execution)

    def get_evidence_upload_url(
        self,
        execution_id: UUID,
        step_id: UUID,
        content_type: str,
    ) -> tuple[str, str]:
        execution = self._exec_repo.get(execution_id)
        if execution is None:
            raise NotFoundError("Execution", str(execution_id))

        key = f"evidence/{self._context.tenant_id}/{execution_id}/{step_id}"
        upload_url = self._storage.generate_upload_url(key, content_type)
        return upload_url, key

    def list_executions(
        self,
        task_id: UUID | None = None,
        status: ExecutionStatus | None = None,
    ) -> list[Execution]:
        return self._exec_repo.list(task_id=task_id, status=status)

    def get_execution(self, execution_id: UUID) -> Execution:
        execution = self._exec_repo.get_with_steps(execution_id)
        if execution is None:
            raise NotFoundError("Execution", str(execution_id))
        return execution
