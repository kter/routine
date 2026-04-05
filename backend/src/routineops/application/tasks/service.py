from __future__ import annotations

import logging
from datetime import UTC, datetime, timezone
from uuid import UUID, uuid4

import pytz

from routineops.app.request_context import RequestContext
from routineops.application.tasks.ports import TaskRepositoryPort
from routineops.domain.entities.task import Step, Task
from routineops.domain.exceptions import NotFoundError
from routineops.domain.value_objects.cron_expression import CronExpression
from routineops.domain.value_objects.evidence_type import EvidenceType
from routineops.infrastructure.monitoring.logging import emit_structured_log

logger = logging.getLogger(__name__)


class TaskService:
    def __init__(self, repo: TaskRepositoryPort, context: RequestContext) -> None:
        self._repo = repo
        self._context = context

    def list_tasks(self, active_only: bool = False) -> list[Task]:
        return self._repo.list(active_only=active_only)

    def get_task(self, task_id: UUID) -> Task:
        task = self._repo.get_with_steps(task_id)
        if task is None:
            raise NotFoundError("Task", str(task_id))
        return task

    def create_task(
        self,
        title: str,
        cron_expression: str,
        description: str = "",
        timezone: str = "Asia/Tokyo",
        estimated_minutes: int = 30,
        tags: list[str] | None = None,
        steps: list[dict[str, object]] | None = None,
    ) -> Task:
        cron = CronExpression(cron_expression)
        now = datetime.now(tz=timezone_utc())
        normalized_timezone = normalize_timezone_name(timezone)

        task = Task(
            id=uuid4(),
            tenant_id=self._context.tenant_id,
            title=title,
            description=description,
            cron_expression=cron,
            timezone=normalized_timezone,
            estimated_minutes=estimated_minutes,
            is_active=True,
            tags=tags or [],
            metadata={},
            created_by=self._context.user_sub,
            created_at=now,
            updated_at=now,
        )

        if steps:
            task.steps = self._build_steps(self._context.tenant_id, task.id, steps, now)

        created_task = self._repo.create(task)
        emit_structured_log(
            logger,
            logging.INFO,
            "Task created",
            event_name="task_mutated",
            action="create",
            task_id=str(created_task.id),
            step_count=len(created_task.steps),
            outcome="success",
        )
        return created_task

    def update_task(
        self,
        task_id: UUID,
        **kwargs: object,
    ) -> Task:
        task = self._repo.get_with_steps(task_id)
        if task is None:
            raise NotFoundError("Task", str(task_id))

        has_steps_update = "steps" in kwargs
        steps_to_update = kwargs.pop("steps") if has_steps_update else None
        if "cron_expression" in kwargs:
            kwargs["cron_expression"] = CronExpression(str(kwargs["cron_expression"]))
        if "timezone" in kwargs:
            kwargs["timezone"] = normalize_timezone_name(kwargs["timezone"])

        for key, value in kwargs.items():
            if hasattr(task, key):
                object.__setattr__(task, key, value)

        now = datetime.now(tz=timezone_utc())

        if has_steps_update:
            task.steps = self._build_steps(
                self._context.tenant_id,
                task.id,
                self._validate_steps_payload(steps_to_update),
                now,
            )

        task.updated_at = now
        updated_task = self._repo.update(task)
        updated_fields = sorted(
            [
                *[str(key) for key in kwargs.keys()],
                *(["steps"] if has_steps_update else []),
            ]
        )
        emit_structured_log(
            logger,
            logging.INFO,
            "Task updated",
            event_name="task_mutated",
            action="update",
            task_id=str(updated_task.id),
            changed_fields=updated_fields,
            step_count=len(updated_task.steps),
            outcome="success",
        )
        return updated_task

    def delete_task(self, task_id: UUID) -> None:
        task = self._repo.get(task_id)
        if task is None:
            raise NotFoundError("Task", str(task_id))
        self._repo.delete(task_id)
        emit_structured_log(
            logger,
            logging.INFO,
            "Task deleted",
            event_name="task_mutated",
            action="delete",
            task_id=str(task_id),
            outcome="success",
        )

    def _build_steps(
        self,
        tenant_id: UUID,
        task_id: UUID,
        steps_data: list[dict[str, object]],
        now: datetime,
    ) -> list[Step]:
        steps: list[Step] = []
        for step_data in steps_data:
            steps.append(
                Step(
                    id=uuid4(),
                    tenant_id=tenant_id,
                    task_id=task_id,
                    position=int(str(step_data.get("position", 1))),
                    title=str(step_data["title"]),
                    instruction=str(step_data.get("instruction", "")),
                    evidence_type=EvidenceType(str(step_data.get("evidence_type", "none"))),
                    is_required=bool(step_data.get("is_required", True)),
                    created_at=now,
                    updated_at=now,
                )
            )
        return steps

    def _validate_steps_payload(self, steps_data: object) -> list[dict[str, object]]:
        if not isinstance(steps_data, list):
            raise TypeError("steps must be a list")

        step_payloads: list[dict[str, object]] = []
        for step_data in steps_data:
            if not isinstance(step_data, dict):
                raise TypeError("steps must be a list of objects")
            step_payloads.append(step_data)
        return step_payloads


def timezone_utc() -> timezone:
    return UTC


def normalize_timezone_name(value: object) -> str:
    timezone_name = str(value or "").strip() or "Asia/Tokyo"
    try:
        pytz.timezone(timezone_name)
    except pytz.UnknownTimeZoneError:
        return "Asia/Tokyo"
    return timezone_name
