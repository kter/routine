import logging
from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytz
from croniter import croniter
from pytz import BaseTzInfo

from routineops.domain.entities.task import Task
from routineops.domain.value_objects.execution_status import ExecutionStatus
from routineops.usecases.interfaces.execution_repository import ExecutionRepositoryPort
from routineops.usecases.interfaces.task_repository import TaskRepositoryPort

logger = logging.getLogger(__name__)


class DashboardItem:
    def __init__(
        self,
        task_id: UUID,
        title: str,
        scheduled_for: datetime,
        estimated_minutes: int,
        execution_id: UUID | None = None,
        status: str | None = None,
    ) -> None:
        self.task_id = task_id
        self.title = title
        self.scheduled_for = scheduled_for
        self.estimated_minutes = estimated_minutes
        self.execution_id = execution_id
        self.status = status


class DashboardData:
    def __init__(
        self,
        today: list[DashboardItem],
        overdue: list[DashboardItem],
        upcoming: list[DashboardItem],
    ) -> None:
        self.today = today
        self.overdue = overdue
        self.upcoming = upcoming


class DashboardUsecases:
    def __init__(
        self,
        task_repo: TaskRepositoryPort,
        exec_repo: ExecutionRepositoryPort,
    ) -> None:
        self._task_repo = task_repo
        self._exec_repo = exec_repo

    def get_dashboard(self, tenant_id: UUID) -> DashboardData:
        now_utc = datetime.now(tz=UTC)
        search_start = now_utc - timedelta(days=7)
        week_end = now_utc + timedelta(days=8)

        tasks = self._task_repo.list(tenant_id, active_only=True)

        # Get recent executions to check statuses
        executions = self._exec_repo.list(tenant_id)
        exec_by_task: dict[UUID, list] = {}
        for e in executions:
            exec_by_task.setdefault(e.task_id, []).append(e)

        today_items: list[DashboardItem] = []
        overdue_items: list[DashboardItem] = []
        upcoming_items: list[DashboardItem] = []

        for task in tasks:
            task_tz = _resolve_task_timezone(task.timezone)
            today_local = now_utc.astimezone(task_tz).date()
            occurrences = self._get_upcoming_occurrences(
                task, search_start, week_end
            )
            task_execs = exec_by_task.get(task.id, [])

            for occ in occurrences:
                # Check if there's an execution for this occurrence
                matching_exec = self._find_matching_execution(occ, task_execs)

                item = DashboardItem(
                    task_id=task.id,
                    title=task.title,
                    scheduled_for=occ,
                    estimated_minutes=task.estimated_minutes,
                    execution_id=matching_exec.id if matching_exec else None,
                    status=matching_exec.status if matching_exec else None,
                )

                occ_local = occ.astimezone(task_tz).date()

                if occ_local < today_local:
                    # Overdue: past occurrences without completed execution
                    if not matching_exec or matching_exec.status == ExecutionStatus.IN_PROGRESS:
                        overdue_items.append(item)
                elif occ_local == today_local:
                    today_items.append(item)
                else:
                    upcoming_items.append(item)

        return DashboardData(
            today=sorted(today_items, key=lambda x: x.scheduled_for),
            overdue=sorted(overdue_items, key=lambda x: x.scheduled_for),
            upcoming=sorted(upcoming_items, key=lambda x: x.scheduled_for)[:20],
        )

    def _get_upcoming_occurrences(
        self, task: Task, start: datetime, end: datetime
    ) -> list[datetime]:
        try:
            tz = _resolve_task_timezone(task.timezone)
            start_local = start.astimezone(tz)
            cron = croniter(str(task.cron_expression), start_local - timedelta(seconds=1))
            occurrences = []
            while True:
                occ = cron.get_next(datetime)
                if occ.tzinfo is None:
                    occ = tz.localize(occ)
                occ_utc = occ.astimezone(UTC)
                if occ_utc > end:
                    break
                occurrences.append(occ_utc)
            return occurrences
        except Exception:
            return []

    def _find_matching_execution(self, scheduled_for: datetime, executions: list) -> object | None:
        # Find execution within 1 hour window of the scheduled time
        window = timedelta(hours=1)
        for e in executions:
            if e.scheduled_for and abs(
                (e.scheduled_for - scheduled_for).total_seconds()
            ) < window.total_seconds():
                return e
        return None


def _resolve_task_timezone(timezone_name: str | None) -> BaseTzInfo:
    normalized = (timezone_name or "").strip() or "Asia/Tokyo"
    try:
        return pytz.timezone(normalized)
    except pytz.UnknownTimeZoneError:
        logger.warning(
            "Invalid task timezone %r; falling back to Asia/Tokyo",
            timezone_name,
        )
        return pytz.timezone("Asia/Tokyo")
