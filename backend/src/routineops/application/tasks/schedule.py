from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta

import pytz
from croniter import croniter
from pytz import BaseTzInfo

from routineops.domain.entities.task import Task

logger = logging.getLogger(__name__)


def resolve_task_timezone(timezone_name: str | None) -> BaseTzInfo:
    normalized = (timezone_name or "").strip() or "Asia/Tokyo"
    try:
        return pytz.timezone(normalized)
    except pytz.UnknownTimeZoneError:
        logger.warning(
            "Invalid task timezone %r; falling back to Asia/Tokyo",
            timezone_name,
        )
        return pytz.timezone("Asia/Tokyo")


def get_occurrences(task: Task, start: datetime, end: datetime) -> list[datetime]:
    try:
        tz = resolve_task_timezone(task.timezone)
        start_local = start.astimezone(tz)
        cron = croniter(str(task.cron_expression), start_local - timedelta(seconds=1))
        occurrences: list[datetime] = []
        while True:
            occurrence = cron.get_next(datetime)
            if occurrence.tzinfo is None:
                occurrence = tz.localize(occurrence)
            occurrence_utc = occurrence.astimezone(UTC)
            if occurrence_utc > end:
                break
            occurrences.append(occurrence_utc)
        return occurrences
    except Exception:
        return []
