"""Unit tests for TaskUsecases with mocked repository."""

from datetime import UTC, datetime
from unittest.mock import MagicMock
from uuid import UUID, uuid4

import pytest

from routineops.app.request_context import RequestContext
from routineops.domain.entities.task import Step, Task
from routineops.domain.exceptions import NotFoundError, ValidationError
from routineops.domain.value_objects.cron_expression import CronExpression
from routineops.domain.value_objects.evidence_type import EvidenceType
from routineops.usecases.interfaces.task_repository import TaskRepositoryPort
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
        created_at=datetime.now(tz=UTC),
        updated_at=datetime.now(tz=UTC),
        steps=[],
    )


def make_step(
    task_id: UUID,
    *,
    title: str = "確認ステップ",
    instruction: str = "ログを確認してください",
    evidence_type: EvidenceType = EvidenceType.TEXT,
    is_required: bool = True,
    position: int = 1,
) -> Step:
    return Step(
        id=uuid4(),
        tenant_id=TENANT_ID,
        task_id=task_id,
        position=position,
        title=title,
        instruction=instruction,
        evidence_type=evidence_type,
        is_required=is_required,
        created_at=datetime.now(tz=UTC),
        updated_at=datetime.now(tz=UTC),
    )


@pytest.fixture
def mock_repo() -> MagicMock:
    return MagicMock(spec=TaskRepositoryPort)


@pytest.fixture
def request_context() -> RequestContext:
    return RequestContext(tenant_id=TENANT_ID, user_sub=USER_SUB)


@pytest.fixture
def usecases(mock_repo: MagicMock, request_context: RequestContext) -> TaskUsecases:
    return TaskUsecases(mock_repo, request_context)


class TestListTasks:
    def test_delegates_to_repo(self, usecases: TaskUsecases, mock_repo: MagicMock) -> None:
        task = make_task()
        mock_repo.list.return_value = [task]

        result = usecases.list_tasks()

        mock_repo.list.assert_called_once_with(TENANT_ID, active_only=False)
        assert result == [task]

    def test_active_only_flag(self, usecases: TaskUsecases, mock_repo: MagicMock) -> None:
        mock_repo.list.return_value = []
        usecases.list_tasks(active_only=True)
        mock_repo.list.assert_called_once_with(TENANT_ID, active_only=True)


class TestGetTask:
    def test_returns_task_when_found(self, usecases: TaskUsecases, mock_repo: MagicMock) -> None:
        task = make_task()
        mock_repo.get_with_steps.return_value = task

        result = usecases.get_task(task.id)

        assert result == task

    def test_raises_not_found_when_missing(
        self, usecases: TaskUsecases, mock_repo: MagicMock
    ) -> None:
        mock_repo.get_with_steps.return_value = None
        task_id = uuid4()

        with pytest.raises(NotFoundError, match="Task"):
            usecases.get_task(task_id)


class TestCreateTask:
    def test_creates_task_with_valid_cron(
        self, usecases: TaskUsecases, mock_repo: MagicMock
    ) -> None:
        task = make_task()
        mock_repo.create.return_value = task

        result = usecases.create_task(
            title="月次パッチ",
            cron_expression="0 10 1 * *",
        )

        mock_repo.create.assert_called_once()
        assert result == task

    def test_raises_validation_for_invalid_cron(
        self, usecases: TaskUsecases, mock_repo: MagicMock
    ) -> None:
        with pytest.raises(ValidationError):
            usecases.create_task(
                title="Test",
                cron_expression="invalid",
            )

    def test_creates_steps_when_provided(
        self, usecases: TaskUsecases, mock_repo: MagicMock
    ) -> None:
        mock_repo.create.side_effect = lambda created_task: created_task

        result = usecases.create_task(
            title="テストタスク",
            cron_expression="0 10 * * *",
            steps=[{"position": 1, "title": "確認ステップ"}],
        )

        created_task = mock_repo.create.call_args.args[0]
        assert len(created_task.steps) == 1
        assert created_task.steps[0].title == "確認ステップ"
        assert created_task.steps[0].instruction == ""
        assert created_task.steps[0].evidence_type == EvidenceType.NONE
        assert created_task.steps[0].is_required is True
        assert result.steps == created_task.steps

    def test_uses_single_create_repository_api_for_steps(
        self, usecases: TaskUsecases, mock_repo: MagicMock
    ) -> None:
        mock_repo.create.side_effect = lambda created_task: created_task

        usecases.create_task(
            title="集約作成タスク",
            cron_expression="0 10 * * *",
            steps=[{"position": 1, "title": "集約手順"}],
        )

        mock_repo.create.assert_called_once()

    def test_normalizes_blank_timezone_to_asia_tokyo(
        self, usecases: TaskUsecases, mock_repo: MagicMock
    ) -> None:
        mock_repo.create.side_effect = lambda created_task: created_task

        result = usecases.create_task(
            title="timezone test",
            cron_expression="0 10 * * *",
            timezone="",
        )

        assert result.timezone == "Asia/Tokyo"


class TestDeleteTask:
    def test_deletes_existing_task(self, usecases: TaskUsecases, mock_repo: MagicMock) -> None:
        task = make_task()
        mock_repo.get.return_value = task

        usecases.delete_task(task.id)

        mock_repo.delete.assert_called_once_with(TENANT_ID, task.id)

    def test_raises_not_found_for_missing_task(
        self, usecases: TaskUsecases, mock_repo: MagicMock
    ) -> None:
        mock_repo.get.return_value = None

        with pytest.raises(NotFoundError):
            usecases.delete_task(uuid4())


class TestUpdateTask:
    def test_distinguishes_omitted_steps_from_explicit_empty_list(
        self, usecases: TaskUsecases, mock_repo: MagicMock
    ) -> None:
        kept_task = make_task()
        kept_step = make_step(kept_task.id, title="保持対象")
        kept_task.steps = [kept_step]

        cleared_task = make_task()
        cleared_task.steps = [make_step(cleared_task.id, title="削除対象")]

        mock_repo.get_with_steps.side_effect = [kept_task, cleared_task]
        mock_repo.update.side_effect = lambda updated_task: updated_task

        kept_result = usecases.update_task(kept_task.id, title="手順は保持")
        cleared_result = usecases.update_task(cleared_task.id, steps=[])

        kept_update = mock_repo.update.call_args_list[0].args[0]
        cleared_update = mock_repo.update.call_args_list[1].args[0]

        assert kept_update.steps == [kept_step]
        assert kept_result.steps == [kept_step]
        assert cleared_update.steps == []
        assert cleared_result.steps == []

    def test_keeps_existing_steps_when_steps_are_not_provided(
        self, usecases: TaskUsecases, mock_repo: MagicMock
    ) -> None:
        task = make_task()
        existing_step = make_step(
            task.id,
            title="既存手順",
            instruction="保持される説明",
        )
        task.steps = [existing_step]
        mock_repo.get_with_steps.return_value = task
        mock_repo.update.side_effect = lambda updated_task: updated_task

        result = usecases.update_task(task.id, title="更新後タイトル")

        updated_task = mock_repo.update.call_args.args[0]
        assert updated_task.title == "更新後タイトル"
        assert updated_task.steps == [existing_step]
        assert result.steps == [existing_step]

    def test_replaces_steps_with_domain_entities_when_steps_are_provided(
        self, usecases: TaskUsecases, mock_repo: MagicMock
    ) -> None:
        task = make_task()
        task.steps = [make_step(task.id, title="旧手順")]
        replaced_task = make_task(task.id)
        persisted_step = make_step(
            task.id,
            title="新手順",
            instruction="更新後の説明",
            evidence_type=EvidenceType.IMAGE,
            is_required=False,
        )
        replaced_task.steps = [persisted_step]
        mock_repo.get_with_steps.return_value = task
        mock_repo.update.return_value = replaced_task

        result = usecases.update_task(
            task.id,
            steps=[
                {
                    "position": 1,
                    "title": "新手順",
                    "instruction": "更新後の説明",
                    "evidence_type": "image",
                    "is_required": False,
                }
            ],
        )

        updated_task = mock_repo.update.call_args.args[0]
        assert len(updated_task.steps) == 1
        assert isinstance(updated_task.steps[0], Step)
        assert updated_task.steps[0].task_id == task.id
        assert updated_task.steps[0].title == "新手順"
        assert updated_task.steps[0].instruction == "更新後の説明"
        assert updated_task.steps[0].evidence_type == EvidenceType.IMAGE
        assert updated_task.steps[0].is_required is False
        assert updated_task.steps[0].id != persisted_step.id
        assert result.steps == [persisted_step]

    def test_normalizes_blank_timezone_on_update(
        self, usecases: TaskUsecases, mock_repo: MagicMock
    ) -> None:
        task = make_task()
        mock_repo.get_with_steps.return_value = task
        mock_repo.update.side_effect = lambda updated_task: updated_task

        result = usecases.update_task(task.id, timezone="")

        assert result.timezone == "Asia/Tokyo"

    def test_clears_steps_when_empty_list_is_provided(
        self, usecases: TaskUsecases, mock_repo: MagicMock
    ) -> None:
        task = make_task()
        task.steps = [make_step(task.id)]
        mock_repo.get_with_steps.return_value = task
        mock_repo.update.side_effect = lambda updated_task: updated_task

        result = usecases.update_task(task.id, steps=[])

        updated_task = mock_repo.update.call_args.args[0]
        assert updated_task.steps == []
        assert result.steps == []

    def test_uses_same_step_defaults_when_updating(
        self, usecases: TaskUsecases, mock_repo: MagicMock
    ) -> None:
        task = make_task()
        mock_repo.get_with_steps.return_value = task
        mock_repo.update.side_effect = lambda updated_task: updated_task

        result = usecases.update_task(task.id, steps=[{"position": 1, "title": "既定値テスト"}])

        updated_task = mock_repo.update.call_args.args[0]
        assert updated_task.steps[0].instruction == ""
        assert updated_task.steps[0].evidence_type == EvidenceType.NONE
        assert updated_task.steps[0].is_required is True
        assert result.steps[0].title == "既定値テスト"

    def test_uses_single_update_repository_api_when_steps_change(
        self, usecases: TaskUsecases, mock_repo: MagicMock
    ) -> None:
        task = make_task()
        task.steps = [make_step(task.id, title="旧手順")]
        mock_repo.get_with_steps.return_value = task
        mock_repo.update.side_effect = lambda updated_task: updated_task

        result = usecases.update_task(task.id, steps=[{"position": 1, "title": "新手順"}])

        mock_repo.update.assert_called_once()
        assert result.steps[0].title == "新手順"
