from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import MagicMock
from uuid import UUID, uuid4

from routineops.application.queries.dashboard_query_service import DashboardQueryService
from routineops.domain.entities.execution import Execution
from routineops.domain.entities.task import Task
from routineops.domain.value_objects.cron_expression import CronExpression
from routineops.domain.value_objects.execution_status import ExecutionStatus

TENANT_ID = UUID("00000000-0000-0000-0000-000000000001")


def make_task(
    cron: str = "0 10 * * *",
    *,
    timezone: str = "Asia/Tokyo",
    estimated_minutes: int = 30,
) -> Task:
    return Task(
        id=uuid4(),
        tenant_id=TENANT_ID,
        title="テストタスク",
        description="",
        cron_expression=CronExpression(cron),
        timezone=timezone,
        estimated_minutes=estimated_minutes,
        is_active=True,
        tags=[],
        metadata={},
        created_by="user",
        created_at=datetime.now(tz=UTC),
        updated_at=datetime.now(tz=UTC),
        steps=[],
    )


def make_execution(task: Task, *, scheduled_for: datetime, status: ExecutionStatus) -> Execution:
    now = datetime.now(tz=UTC)
    return Execution(
        id=uuid4(),
        tenant_id=TENANT_ID,
        task_id=task.id,
        started_by="user",
        status=status,
        scheduled_for=scheduled_for,
        started_at=now,
        completed_at=None,
        duration_seconds=None,
        notes="",
        metadata={},
        created_at=now,
        updated_at=now,
        steps=[],
    )


def test_query_service_classifies_today_and_overdue_using_task_timezone() -> None:
    task_repo = MagicMock()
    exec_repo = MagicMock()
    task_repo.list.return_value = [make_task()]
    exec_repo.list.return_value = []
    service = DashboardQueryService(task_repo, exec_repo)

    result = service.get_dashboard(
        TENANT_ID,
        now_utc=datetime(2026, 3, 10, 23, 0, tzinfo=UTC),
    )

    assert datetime(2026, 3, 10, 1, 0, tzinfo=UTC) in {
        item.scheduled_for for item in result.overdue
    }
    assert datetime(2026, 3, 11, 1, 0, tzinfo=UTC) in {item.scheduled_for for item in result.today}
    exec_repo.list.assert_called_once_with(
        TENANT_ID,
        scheduled_from=datetime(2026, 3, 3, 23, 0, tzinfo=UTC),
        scheduled_to=datetime(2026, 3, 18, 23, 0, tzinfo=UTC),
    )


def test_query_service_attaches_matching_execution_metadata() -> None:
    task_repo = MagicMock()
    exec_repo = MagicMock()
    task = make_task(cron="0 10 * * *", timezone="UTC", estimated_minutes=45)
    scheduled_for = datetime(2026, 3, 13, 10, 0, tzinfo=UTC)
    task_repo.list.return_value = [task]
    exec_repo.list.return_value = [
        make_execution(
            task,
            scheduled_for=scheduled_for.replace(tzinfo=None),
            status=ExecutionStatus.IN_PROGRESS,
        )
    ]
    service = DashboardQueryService(task_repo, exec_repo)

    result = service.get_dashboard(
        TENANT_ID,
        now_utc=datetime(2026, 3, 13, 8, 0, tzinfo=UTC),
    )

    matched_item = next(item for item in result.today if item.task_id == task.id)
    assert matched_item.execution_id is not None
    assert matched_item.status == ExecutionStatus.IN_PROGRESS
    assert matched_item.estimated_minutes == 45


def test_query_service_caps_upcoming_items_to_twenty() -> None:
    task_repo = MagicMock()
    exec_repo = MagicMock()
    task_repo.list.return_value = [make_task(cron="0 * * * *", timezone="UTC")]
    exec_repo.list.return_value = []
    service = DashboardQueryService(task_repo, exec_repo)

    result = service.get_dashboard(
        TENANT_ID,
        now_utc=datetime(2026, 3, 1, 8, 0, tzinfo=UTC),
    )

    assert len(result.upcoming) == 20


def test_query_service_reads_only_execution_window() -> None:
    task_repo = MagicMock()
    exec_repo = MagicMock()
    task_repo.list.return_value = [make_task(timezone="UTC")]
    exec_repo.list.return_value = []
    service = DashboardQueryService(task_repo, exec_repo)
    now = datetime(2026, 3, 15, 12, 30, tzinfo=UTC)

    service.get_dashboard(TENANT_ID, now_utc=now)

    exec_repo.list.assert_called_once_with(
        TENANT_ID,
        scheduled_from=datetime(2026, 3, 8, 12, 30, tzinfo=UTC),
        scheduled_to=datetime(2026, 3, 23, 12, 30, tzinfo=UTC),
    )
