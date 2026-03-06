"""Unit tests for ExecutionStatus and StepStatus value objects."""

import pytest

from routineops.domain.value_objects.execution_status import ExecutionStatus, StepStatus


class TestExecutionStatus:
    def test_values(self) -> None:
        assert ExecutionStatus.IN_PROGRESS == "in_progress"
        assert ExecutionStatus.COMPLETED == "completed"
        assert ExecutionStatus.ABANDONED == "abandoned"

    def test_from_string(self) -> None:
        assert ExecutionStatus("in_progress") == ExecutionStatus.IN_PROGRESS
        assert ExecutionStatus("completed") == ExecutionStatus.COMPLETED
        assert ExecutionStatus("abandoned") == ExecutionStatus.ABANDONED

    def test_invalid_raises(self) -> None:
        with pytest.raises(ValueError):
            ExecutionStatus("invalid_status")


class TestStepStatus:
    def test_values(self) -> None:
        assert StepStatus.PENDING == "pending"
        assert StepStatus.COMPLETED == "completed"
        assert StepStatus.SKIPPED == "skipped"

    def test_from_string(self) -> None:
        assert StepStatus("pending") == StepStatus.PENDING

    def test_invalid_raises(self) -> None:
        with pytest.raises(ValueError):
            StepStatus("bad_value")
