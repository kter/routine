"""Unit tests for TaskUsecases with mocked repository."""

from datetime import datetime, timezone
from unittest.mock import MagicMock
from uuid import UUID, uuid4

import pytest

from routineops.domain.entities.task import Task
from routineops.domain.exceptions import NotFoundError, ValidationError
from routineops.domain.value_objects.cron_expression import CronExpression
from routineops.usecases.task_usecases import TaskUsecases


TENANT_ID = UUID("00000000-0000-0000-0000-000000000001")
USER_SUB = "user-sub-123"


def make_task(task_id: UUID | None = None) -> Task:
    return Task(
        id=task_id or uuid4(),
        tenant_id=TENANT_ID,
        title="月次セキュリティパッチ確認",
        description="",
        cron_expression=CronExpression("0 10 1 * *"),
        timezone="Asia/Tokyo",
        estimated_minutes=60,
        is_active=True,
        tags=["security"],
        metadata={},
        created_by=USER_SUB,
        created_at=datetime.now(tz=timezone.utc),
        updated_at=datetime.now(tz=timezone.utc),
        steps=[],
    )


@pytest.fixture
def mock_repo() -> MagicMock:
    return MagicMock()


@pytest.fixture
def usecases(mock_repo: MagicMock) -> TaskUsecases:
    return TaskUsecases(mock_repo)


class TestListTasks:
    def test_delegates_to_repo(self, usecases: TaskUsecases, mock_repo: MagicMock) -> None:
        task = make_task()
        mock_repo.list.return_value = [task]

        result = usecases.list_tasks(TENANT_ID)

        mock_repo.list.assert_called_once_with(TENANT_ID, active_only=False)
        assert result == [task]

    def test_active_only_flag(self, usecases: TaskUsecases, mock_repo: MagicMock) -> None:
        mock_repo.list.return_value = []
        usecases.list_tasks(TENANT_ID, active_only=True)
        mock_repo.list.assert_called_once_with(TENANT_ID, active_only=True)


class TestGetTask:
    def test_returns_task_when_found(self, usecases: TaskUsecases, mock_repo: MagicMock) -> None:
        task = make_task()
        mock_repo.get_with_steps.return_value = task

        result = usecases.get_task(TENANT_ID, task.id)

        assert result == task

    def test_raises_not_found_when_missing(
        self, usecases: TaskUsecases, mock_repo: MagicMock
    ) -> None:
        mock_repo.get_with_steps.return_value = None
        task_id = uuid4()

        with pytest.raises(NotFoundError, match="Task"):
            usecases.get_task(TENANT_ID, task_id)


class TestCreateTask:
    def test_creates_task_with_valid_cron(
        self, usecases: TaskUsecases, mock_repo: MagicMock
    ) -> None:
        task = make_task()
        mock_repo.create.return_value = task

        result = usecases.create_task(
            tenant_id=TENANT_ID,
            title="月次パッチ",
            cron_expression="0 10 1 * *",
            created_by=USER_SUB,
        )

        mock_repo.create.assert_called_once()
        assert result == task

    def test_raises_validation_for_invalid_cron(
        self, usecases: TaskUsecases, mock_repo: MagicMock
    ) -> None:
        with pytest.raises(ValidationError):
            usecases.create_task(
                tenant_id=TENANT_ID,
                title="Test",
                cron_expression="invalid",
                created_by=USER_SUB,
            )

    def test_creates_steps_when_provided(
        self, usecases: TaskUsecases, mock_repo: MagicMock
    ) -> None:
        task = make_task()
        task.steps = []
        mock_repo.create.return_value = task

        from routineops.domain.entities.task import Step
        from routineops.domain.value_objects.evidence_type import EvidenceType

        step = Step(
            id=uuid4(),
            tenant_id=TENANT_ID,
            task_id=task.id,
            position=1,
            title="確認ステップ",
            instruction="ログを確認してください",
            evidence_type=EvidenceType.TEXT,
            is_required=True,
            created_at=datetime.now(tz=timezone.utc),
            updated_at=datetime.now(tz=timezone.utc),
        )
        mock_repo.create_step.return_value = step

        usecases.create_task(
            tenant_id=TENANT_ID,
            title="テストタスク",
            cron_expression="0 10 * * *",
            created_by=USER_SUB,
            steps=[{"position": 1, "title": "確認ステップ", "evidence_type": "text"}],
        )

        mock_repo.create_step.assert_called_once()


class TestDeleteTask:
    def test_deletes_existing_task(
        self, usecases: TaskUsecases, mock_repo: MagicMock
    ) -> None:
        task = make_task()
        mock_repo.get.return_value = task

        usecases.delete_task(TENANT_ID, task.id)

        mock_repo.delete.assert_called_once_with(TENANT_ID, task.id)

    def test_raises_not_found_for_missing_task(
        self, usecases: TaskUsecases, mock_repo: MagicMock
    ) -> None:
        mock_repo.get.return_value = None

        with pytest.raises(NotFoundError):
            usecases.delete_task(TENANT_ID, uuid4())
