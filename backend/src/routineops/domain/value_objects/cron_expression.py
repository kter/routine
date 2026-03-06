from dataclasses import dataclass
from croniter import croniter

from routineops.domain.exceptions import ValidationError


@dataclass(frozen=True)
class CronExpression:
    value: str

    def __post_init__(self) -> None:
        if not self.value or not self.value.strip():
            raise ValidationError("Cron expression cannot be empty")
        if not croniter.is_valid(self.value):
            raise ValidationError(f"Invalid cron expression: '{self.value}'")

    def __str__(self) -> str:
        return self.value
