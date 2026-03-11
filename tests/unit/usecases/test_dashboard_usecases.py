"""Unit tests for DashboardUsecases - cron evaluation logic."""

from datetime import UTC, datetime
from unittest.mock import MagicMock, patch
from uuid import UUID, uuid4

import pytest

from routineops.domain.entities.task import Task
from routineops.domain.value_objects.cron_expression import CronExpression
from routineops.usecases.dashboard_usecases import DashboardUsecases

TENANT_ID = UUID("00000000-0000-0000-0000-000000000001")


def make_task(cron: str = "0 10 * * *") -> Task:
    return Task(
        id=uuid4(),
        tenant_id=TENANT_ID,
        title="テストタスク",
        description="",
        cron_expression=CronExpression(cron),
        timezone="Asia/Tokyo",
        estimated_minutes=30,
        is_active=True,
        tags=[],
        metadata={},
        created_by="user",
        created_at=datetime.now(tz=UTC),
        updated_at=datetime.now(tz=UTC),
        steps=[],
    )


@pytest.fixture
def mock_task_repo() -> MagicMock:
    return MagicMock()


@pytest.fixture
def mock_exec_repo() -> MagicMock:
    return MagicMock()


@pytest.fixture
def usecases(mock_task_repo: MagicMock, mock_exec_repo: MagicMock) -> DashboardUsecases:
    return DashboardUsecases(mock_task_repo, mock_exec_repo)


class TestGetDashboard:
    def test_returns_today_tasks_for_daily_cron(
        self,
        usecases: DashboardUsecases,
        mock_task_repo: MagicMock,
        mock_exec_repo: MagicMock,
    ) -> None:
        task = make_task("0 10 * * *")
        mock_task_repo.list.return_value = [task]
        mock_exec_repo.list.return_value = []

        result = usecases.get_dashboard(TENANT_ID)

        # A daily task should appear somewhere: today or upcoming
        all_items = result.today + result.upcoming
        assert any(item.task_id == task.id for item in all_items)

    def test_empty_when_no_tasks(
        self,
        usecases: DashboardUsecases,
        mock_task_repo: MagicMock,
        mock_exec_repo: MagicMock,
    ) -> None:
        mock_task_repo.list.return_value = []
        mock_exec_repo.list.return_value = []

        result = usecases.get_dashboard(TENANT_ID)

        assert result.today == []
        assert result.overdue == []
        assert result.upcoming == []

    def test_inactive_tasks_are_excluded(
        self,
        usecases: DashboardUsecases,
        mock_task_repo: MagicMock,
        mock_exec_repo: MagicMock,
    ) -> None:
        # list() with active_only=True returns empty
        mock_task_repo.list.return_value = []
        mock_exec_repo.list.return_value = []

        result = usecases.get_dashboard(TENANT_ID)

        mock_task_repo.list.assert_called_once_with(TENANT_ID, active_only=True)
        assert result.today == []

    def test_classifies_today_using_task_timezone_not_utc(
        self,
        usecases: DashboardUsecases,
        mock_task_repo: MagicMock,
        mock_exec_repo: MagicMock,
    ) -> None:
        task = make_task("0 10 * * *")
        mock_task_repo.list.return_value = [task]
        mock_exec_repo.list.return_value = []

        fixed_now = datetime(2026, 3, 10, 23, 0, tzinfo=UTC)

        class FixedDateTime(datetime):
            @classmethod
            def now(cls, tz=None):  # type: ignore[override]
                if tz is None:
                    return fixed_now.replace(tzinfo=None)
                return fixed_now.astimezone(tz)

        with patch("routineops.usecases.dashboard_usecases.datetime", FixedDateTime):
            result = usecases.get_dashboard(TENANT_ID)

        assert datetime(2026, 3, 10, 1, 0, tzinfo=UTC) not in {
            item.scheduled_for for item in result.today
        }
        assert datetime(2026, 3, 10, 1, 0, tzinfo=UTC) in {
            item.scheduled_for for item in result.overdue
        }
        assert datetime(2026, 3, 11, 1, 0, tzinfo=UTC) in {
            item.scheduled_for for item in result.today
        }

    def test_falls_back_when_task_timezone_is_blank(
        self,
        usecases: DashboardUsecases,
        mock_task_repo: MagicMock,
        mock_exec_repo: MagicMock,
    ) -> None:
        task = make_task("0 10 * * *")
        task.timezone = ""
        mock_task_repo.list.return_value = [task]
        mock_exec_repo.list.return_value = []

        fixed_now = datetime(2026, 3, 10, 23, 0, tzinfo=UTC)

        class FixedDateTime(datetime):
            @classmethod
            def now(cls, tz=None):  # type: ignore[override]
                if tz is None:
                    return fixed_now.replace(tzinfo=None)
                return fixed_now.astimezone(tz)

        with patch("routineops.usecases.dashboard_usecases.datetime", FixedDateTime):
            result = usecases.get_dashboard(TENANT_ID)

        assert datetime(2026, 3, 11, 1, 0, tzinfo=UTC) in {
            item.scheduled_for for item in result.today
        }
