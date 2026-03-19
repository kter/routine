from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import UUID

from routineops.application.executions.ports import ExecutionRepositoryPort
from routineops.application.tasks.ports import TaskRepositoryPort
from routineops.application.tasks.schedule import get_occurrences, resolve_task_timezone
from routineops.domain.entities.execution import Execution
from routineops.domain.value_objects.execution_status import ExecutionStatus


@dataclass
class DashboardItem:
    task_id: UUID
    title: str
    scheduled_for: datetime
    estimated_minutes: int
    execution_id: UUID | None = None
    status: str | None = None


@dataclass
class DashboardData:
    today: list[DashboardItem]
    overdue: list[DashboardItem]
    upcoming: list[DashboardItem]


class DashboardQueryService:
    def __init__(
        self,
        task_repo: TaskRepositoryPort,
        exec_repo: ExecutionRepositoryPort,
    ) -> None:
        self._task_repo = task_repo
        self._exec_repo = exec_repo

    def get_dashboard(self, *, now_utc: datetime | None = None) -> DashboardData:
        current_time = now_utc or datetime.now(tz=UTC)
        search_start = current_time - timedelta(days=7)
        week_end = current_time + timedelta(days=8)

        tasks = self._task_repo.list(active_only=True)
        executions = self._exec_repo.list(
            scheduled_from=search_start,
            scheduled_to=week_end,
        )
        executions_by_task: dict[UUID, list[Execution]] = {}
        for execution in executions:
            executions_by_task.setdefault(execution.task_id, []).append(execution)

        today_items: list[DashboardItem] = []
        overdue_items: list[DashboardItem] = []
        upcoming_items: list[DashboardItem] = []

        for task in tasks:
            task_timezone = resolve_task_timezone(task.timezone)
            today_local = current_time.astimezone(task_timezone).date()
            occurrences = get_occurrences(task, search_start, week_end)
            task_executions = executions_by_task.get(task.id, [])

            for occurrence in occurrences:
                matching_execution = self._find_matching_execution(occurrence, task_executions)
                item = DashboardItem(
                    task_id=task.id,
                    title=task.title,
                    scheduled_for=occurrence,
                    estimated_minutes=task.estimated_minutes,
                    execution_id=matching_execution.id if matching_execution else None,
                    status=matching_execution.status if matching_execution else None,
                )
                occurrence_local = occurrence.astimezone(task_timezone).date()

                if occurrence_local < today_local:
                    if (
                        matching_execution is None
                        or matching_execution.status == ExecutionStatus.IN_PROGRESS
                    ):
                        overdue_items.append(item)
                elif occurrence_local == today_local:
                    today_items.append(item)
                else:
                    upcoming_items.append(item)

        return DashboardData(
            today=sorted(today_items, key=lambda item: item.scheduled_for),
            overdue=sorted(overdue_items, key=lambda item: item.scheduled_for),
            upcoming=sorted(upcoming_items, key=lambda item: item.scheduled_for)[:20],
        )

    @staticmethod
    def _find_matching_execution(
        scheduled_for: datetime,
        executions: list[Execution],
    ) -> Execution | None:
        window = timedelta(hours=1)
        normalized_schedule = _ensure_aware_utc(scheduled_for)
        for execution in executions:
            if execution.scheduled_for is None:
                continue
            normalized_execution = _ensure_aware_utc(execution.scheduled_for)
            if (
                abs((normalized_execution - normalized_schedule).total_seconds())
                < window.total_seconds()
            ):
                return execution
        return None


def _ensure_aware_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)
