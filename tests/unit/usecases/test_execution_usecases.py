"""Unit tests for ExecutionUsecases - step completion logic."""

from datetime import UTC, datetime
from unittest.mock import MagicMock
from uuid import UUID, uuid4

import pytest

from routineops.domain.entities.execution import Execution, ExecutionStep
from routineops.domain.entities.task import Step, Task
from routineops.domain.exceptions import NotFoundError, ValidationError
from routineops.domain.value_objects.cron_expression import CronExpression
from routineops.domain.value_objects.evidence_type import EvidenceType
from routineops.domain.value_objects.execution_status import ExecutionStatus, StepStatus
from routineops.usecases.execution_usecases import ExecutionUsecases

TENANT_ID = UUID("00000000-0000-0000-0000-000000000001")
USER_SUB = "user-sub-123"


def make_step(
    task_id: UUID,
    position: int = 1,
    evidence_type: EvidenceType = EvidenceType.NONE,
    is_required: bool = True,
) -> Step:
    return Step(
        id=uuid4(),
        tenant_id=TENANT_ID,
        task_id=task_id,
        position=position,
        title=f"ステップ {position}",
        instruction="",
        evidence_type=evidence_type,
        is_required=is_required,
        created_at=datetime.now(tz=UTC),
        updated_at=datetime.now(tz=UTC),
    )


def make_task(steps: list[Step] | None = None) -> Task:
    task_id = uuid4()
    return Task(
        id=task_id,
        tenant_id=TENANT_ID,
        title="テストタスク",
        description="",
        cron_expression=CronExpression("0 10 * * *"),
        timezone="Asia/Tokyo",
        estimated_minutes=30,
        is_active=True,
        tags=[],
        metadata={},
        created_by=USER_SUB,
        created_at=datetime.now(tz=UTC),
        updated_at=datetime.now(tz=UTC),
        steps=steps or [],
    )


def make_execution(
    task_id: UUID | None = None,
    status: ExecutionStatus = ExecutionStatus.IN_PROGRESS,
    exec_steps: list[ExecutionStep] | None = None,
) -> Execution:
    exec_id = uuid4()
    return Execution(
        id=exec_id,
        tenant_id=TENANT_ID,
        task_id=task_id or uuid4(),
        started_by=USER_SUB,
        status=status,
        scheduled_for=None,
        started_at=datetime.now(tz=UTC),
        completed_at=None,
        duration_seconds=None,
        notes="",
        metadata={},
        created_at=datetime.now(tz=UTC),
        updated_at=datetime.now(tz=UTC),
        steps=exec_steps or [],
    )


def make_exec_step(
    execution_id: UUID,
    step_id: UUID | None = None,
    position: int = 1,
    status: StepStatus = StepStatus.PENDING,
    evidence_type: str = "none",
    is_required: bool = True,
) -> ExecutionStep:
    eid = step_id or uuid4()
    return ExecutionStep(
        id=uuid4(),
        tenant_id=TENANT_ID,
        execution_id=execution_id,
        step_id=eid,
        position=position,
        step_snapshot={
            "title": f"ステップ {position}",
            "instruction": "",
            "evidence_type": evidence_type,
            "is_required": is_required,
        },
        status=status,
        evidence_text=None,
        evidence_image_key=None,
        completed_at=None,
        completed_by=None,
        notes="",
        created_at=datetime.now(tz=UTC),
        updated_at=datetime.now(tz=UTC),
    )


@pytest.fixture
def mock_exec_repo() -> MagicMock:
    return MagicMock()


@pytest.fixture
def mock_task_repo() -> MagicMock:
    return MagicMock()


@pytest.fixture
def mock_storage() -> MagicMock:
    return MagicMock()


@pytest.fixture
def usecases(
    mock_exec_repo: MagicMock,
    mock_task_repo: MagicMock,
    mock_storage: MagicMock,
) -> ExecutionUsecases:
    return ExecutionUsecases(mock_exec_repo, mock_task_repo, mock_storage)


class TestStartExecution:
    def test_creates_execution_with_step_snapshots(
        self,
        usecases: ExecutionUsecases,
        mock_exec_repo: MagicMock,
        mock_task_repo: MagicMock,
    ) -> None:
        task_id = uuid4()
        step = make_step(task_id)
        task = make_task(steps=[step])
        mock_task_repo.get_with_steps.return_value = task

        execution = make_execution(task_id=task_id)
        mock_exec_repo.create.return_value = execution

        exec_step = make_exec_step(execution.id, step_id=step.id)
        mock_exec_repo.create_step.return_value = exec_step

        result = usecases.start_execution(TENANT_ID, task_id, USER_SUB)

        mock_exec_repo.create.assert_called_once()
        mock_exec_repo.create_step.assert_called_once()
        assert len(result.steps) == 1

    def test_raises_not_found_when_task_missing(
        self,
        usecases: ExecutionUsecases,
        mock_task_repo: MagicMock,
    ) -> None:
        mock_task_repo.get_with_steps.return_value = None

        with pytest.raises(NotFoundError, match="Task"):
            usecases.start_execution(TENANT_ID, uuid4(), USER_SUB)

    def test_raises_validation_for_inactive_task(
        self,
        usecases: ExecutionUsecases,
        mock_task_repo: MagicMock,
    ) -> None:
        task = make_task()
        task.is_active = False
        mock_task_repo.get_with_steps.return_value = task

        with pytest.raises(ValidationError, match="not active"):
            usecases.start_execution(TENANT_ID, task.id, USER_SUB)


class TestCompleteStep:
    def test_completes_step_without_evidence(
        self,
        usecases: ExecutionUsecases,
        mock_exec_repo: MagicMock,
    ) -> None:
        execution = make_execution()
        exec_step = make_exec_step(execution.id)
        execution.steps = [exec_step]
        mock_exec_repo.get_with_steps.return_value = execution

        completed_step = make_exec_step(
            execution.id, step_id=exec_step.step_id, status=StepStatus.COMPLETED
        )
        mock_exec_repo.update_step.return_value = completed_step

        result = usecases.complete_step(TENANT_ID, execution.id, exec_step.id, USER_SUB)

        assert result == completed_step
        assert mock_exec_repo.update_step.called
        call_arg = mock_exec_repo.update_step.call_args[0][0]
        assert call_arg.status == StepStatus.COMPLETED
        assert call_arg.completed_by == USER_SUB

    def test_requires_evidence_text_when_evidence_type_is_text(
        self,
        usecases: ExecutionUsecases,
        mock_exec_repo: MagicMock,
    ) -> None:
        execution = make_execution()
        exec_step = make_exec_step(execution.id, evidence_type="text")
        execution.steps = [exec_step]
        mock_exec_repo.get_with_steps.return_value = execution

        with pytest.raises(ValidationError, match="Evidence text is required"):
            usecases.complete_step(
                TENANT_ID,
                execution.id,
                exec_step.id,
                USER_SUB,
                evidence_text=None,
            )

    def test_cannot_complete_already_completed_step(
        self,
        usecases: ExecutionUsecases,
        mock_exec_repo: MagicMock,
    ) -> None:
        execution = make_execution()
        exec_step = make_exec_step(execution.id, status=StepStatus.COMPLETED)
        execution.steps = [exec_step]
        mock_exec_repo.get_with_steps.return_value = execution

        with pytest.raises(ValidationError, match="already"):
            usecases.complete_step(TENANT_ID, execution.id, exec_step.id, USER_SUB)


class TestCompleteExecution:
    def test_completes_when_all_required_steps_done(
        self,
        usecases: ExecutionUsecases,
        mock_exec_repo: MagicMock,
    ) -> None:
        execution = make_execution()
        exec_step = make_exec_step(execution.id, status=StepStatus.COMPLETED)
        execution.steps = [exec_step]
        mock_exec_repo.get_with_steps.return_value = execution

        completed_exec = make_execution(status=ExecutionStatus.COMPLETED)
        mock_exec_repo.update.return_value = completed_exec

        result = usecases.complete_execution(TENANT_ID, execution.id)

        assert result == completed_exec
        call_arg = mock_exec_repo.update.call_args[0][0]
        assert call_arg.status == ExecutionStatus.COMPLETED

    def test_raises_when_required_step_pending(
        self,
        usecases: ExecutionUsecases,
        mock_exec_repo: MagicMock,
    ) -> None:
        execution = make_execution()
        exec_step = make_exec_step(execution.id, status=StepStatus.PENDING, is_required=True)
        execution.steps = [exec_step]
        mock_exec_repo.get_with_steps.return_value = execution

        with pytest.raises(ValidationError, match="required step"):
            usecases.complete_execution(TENANT_ID, execution.id)


class TestSkipStep:
    def test_skips_optional_step(
        self,
        usecases: ExecutionUsecases,
        mock_exec_repo: MagicMock,
    ) -> None:
        execution = make_execution()
        exec_step = make_exec_step(execution.id, is_required=False)
        execution.steps = [exec_step]
        mock_exec_repo.get_with_steps.return_value = execution

        skipped_step = make_exec_step(
            execution.id, step_id=exec_step.step_id, status=StepStatus.SKIPPED
        )
        mock_exec_repo.update_step.return_value = skipped_step

        usecases.skip_step(TENANT_ID, execution.id, exec_step.id)

        call_arg = mock_exec_repo.update_step.call_args[0][0]
        assert call_arg.status == StepStatus.SKIPPED

    def test_cannot_skip_required_step(
        self,
        usecases: ExecutionUsecases,
        mock_exec_repo: MagicMock,
    ) -> None:
        execution = make_execution()
        exec_step = make_exec_step(execution.id, is_required=True)
        execution.steps = [exec_step]
        mock_exec_repo.get_with_steps.return_value = execution

        with pytest.raises(ValidationError, match="Cannot skip a required step"):
            usecases.skip_step(TENANT_ID, execution.id, exec_step.id)
