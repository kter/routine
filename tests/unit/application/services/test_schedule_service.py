from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from routineops.application.services.schedule_service import (
    get_occurrences,
    resolve_task_timezone,
)
from routineops.domain.entities.task import Task
from routineops.domain.value_objects.cron_expression import CronExpression

TENANT_ID = UUID("00000000-0000-0000-0000-000000000001")


def make_task(cron: str = "0 10 * * *", *, timezone: str = "Asia/Tokyo") -> Task:
    return Task(
        id=uuid4(),
        tenant_id=TENANT_ID,
        title="task",
        description="",
        cron_expression=CronExpression(cron),
        timezone=timezone,
        estimated_minutes=30,
        is_active=True,
        tags=[],
        metadata={},
        created_by="user",
        created_at=datetime.now(tz=UTC),
        updated_at=datetime.now(tz=UTC),
        steps=[],
    )


def test_resolve_task_timezone_falls_back_for_blank_values() -> None:
    timezone = resolve_task_timezone("")

    assert timezone.zone == "Asia/Tokyo"


def test_get_occurrences_returns_utc_times_for_task_timezone() -> None:
    task = make_task("0 10 * * *", timezone="Asia/Tokyo")

    occurrences = get_occurrences(
        task,
        start=datetime(2026, 3, 10, 0, 0, tzinfo=UTC),
        end=datetime(2026, 3, 12, 0, 0, tzinfo=UTC),
    )

    assert datetime(2026, 3, 10, 1, 0, tzinfo=UTC) in occurrences
    assert datetime(2026, 3, 11, 1, 0, tzinfo=UTC) in occurrences
