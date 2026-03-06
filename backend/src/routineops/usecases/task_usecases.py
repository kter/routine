from datetime import datetime, timezone
from uuid import UUID, uuid4

from routineops.domain.entities.task import Task, Step
from routineops.domain.exceptions import NotFoundError, ValidationError
from routineops.domain.value_objects.cron_expression import CronExpression
from routineops.domain.value_objects.evidence_type import EvidenceType
from routineops.usecases.interfaces.task_repository import TaskRepositoryPort


class TaskUsecases:
    def __init__(self, repo: TaskRepositoryPort) -> None:
        self._repo = repo

    def list_tasks(self, tenant_id: UUID, active_only: bool = False) -> list[Task]:
        return self._repo.list(tenant_id, active_only=active_only)

    def get_task(self, tenant_id: UUID, task_id: UUID) -> Task:
        task = self._repo.get_with_steps(tenant_id, task_id)
        if task is None:
            raise NotFoundError("Task", str(task_id))
        return task

    def create_task(
        self,
        tenant_id: UUID,
        title: str,
        cron_expression: str,
        created_by: str,
        description: str = "",
        timezone: str = "Asia/Tokyo",
        estimated_minutes: int = 30,
        tags: list[str] | None = None,
        steps: list[dict[str, object]] | None = None,
    ) -> Task:
        cron = CronExpression(cron_expression)
        now = datetime.now(tz=timezone_utc())

        task = Task(
            id=uuid4(),
            tenant_id=tenant_id,
            title=title,
            description=description,
            cron_expression=cron,
            timezone=timezone,
            estimated_minutes=estimated_minutes,
            is_active=True,
            tags=tags or [],
            metadata={},
            created_by=created_by,
            created_at=now,
            updated_at=now,
        )

        created_task = self._repo.create(task)

        if steps:
            created_task.steps = []
            for step_data in steps:
                step = Step(
                    id=uuid4(),
                    tenant_id=tenant_id,
                    task_id=created_task.id,
                    position=int(str(step_data.get("position", 1))),
                    title=str(step_data["title"]),
                    instruction=str(step_data.get("instruction", "")),
                    evidence_type=EvidenceType(step_data.get("evidence_type", "none")),
                    is_required=bool(step_data.get("is_required", True)),
                    created_at=now,
                    updated_at=now,
                )
                created_step = self._repo.create_step(step)
                created_task.steps.append(created_step)

        return created_task

    def update_task(
        self,
        tenant_id: UUID,
        task_id: UUID,
        **kwargs: object,
    ) -> Task:
        task = self._repo.get_with_steps(tenant_id, task_id)
        if task is None:
            raise NotFoundError("Task", str(task_id))

        if "cron_expression" in kwargs:
            kwargs["cron_expression"] = CronExpression(str(kwargs["cron_expression"]))

        for key, value in kwargs.items():
            if hasattr(task, key):
                object.__setattr__(task, key, value)

        task.updated_at = datetime.now(tz=timezone_utc())
        return self._repo.update(task)

    def delete_task(self, tenant_id: UUID, task_id: UUID) -> None:
        task = self._repo.get(tenant_id, task_id)
        if task is None:
            raise NotFoundError("Task", str(task_id))
        self._repo.delete(tenant_id, task_id)


def timezone_utc() -> timezone:
    return timezone.utc
