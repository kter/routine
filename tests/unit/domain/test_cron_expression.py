"""Unit tests for CronExpression value object."""

import pytest

from routineops.domain.exceptions import ValidationError
from routineops.domain.value_objects.cron_expression import CronExpression


class TestCronExpression:
    def test_valid_every_day(self) -> None:
        cron = CronExpression("0 10 * * *")
        assert str(cron) == "0 10 * * *"

    def test_valid_weekly(self) -> None:
        cron = CronExpression("0 10 * * 1")
        assert str(cron) == "0 10 * * 1"

    def test_valid_monthly(self) -> None:
        cron = CronExpression("0 10 1 * *")
        assert str(cron) == "0 10 1 * *"

    def test_valid_weekday(self) -> None:
        cron = CronExpression("0 9 * * 1-5")
        assert str(cron) == "0 9 * * 1-5"

    def test_invalid_expression_raises(self) -> None:
        with pytest.raises(ValidationError, match="Invalid cron expression"):
            CronExpression("not-a-cron")

    def test_empty_expression_raises(self) -> None:
        with pytest.raises(ValidationError, match="cannot be empty"):
            CronExpression("")

    def test_whitespace_only_raises(self) -> None:
        with pytest.raises(ValidationError, match="cannot be empty"):
            CronExpression("   ")

    def test_too_few_fields_raises(self) -> None:
        with pytest.raises(ValidationError):
            CronExpression("0 10 *")

    def test_frozen(self) -> None:
        cron = CronExpression("0 10 * * *")
        with pytest.raises((AttributeError, TypeError)):
            cron.value = "0 11 * * *"  # type: ignore[misc]

    def test_equality(self) -> None:
        assert CronExpression("0 10 * * *") == CronExpression("0 10 * * *")
        assert CronExpression("0 10 * * *") != CronExpression("0 11 * * *")
