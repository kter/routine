from __future__ import annotations

import json
import logging

from routineops.infrastructure.monitoring.logging import (
    JsonFormatter,
    bind_log_context,
    mask_email,
    reset_log_context,
)


def test_json_formatter_includes_context_and_structured_fields() -> None:
    formatter = JsonFormatter(environment="test", component="api")
    token = bind_log_context(
        request_id="req-123",
        tenant_id="tenant-123",
        user_sub="user-123",
    )
    logger = logging.getLogger("routineops.test")

    try:
        record = logger.makeRecord(
            "routineops.test",
            logging.INFO,
            __file__,
            1,
            "Task created",
            args=(),
            exc_info=None,
            extra={
                "event_name": "task_mutated",
                "action": "create",
                "task_id": "task-123",
                "outcome": "success",
            },
        )
        payload = json.loads(formatter.format(record))
    finally:
        reset_log_context(token)

    assert payload["event_name"] == "task_mutated"
    assert payload["service"] == "routineops"
    assert payload["environment"] == "test"
    assert payload["component"] == "api"
    assert payload["request_id"] == "req-123"
    assert payload["tenant_id"] == "tenant-123"
    assert payload["user_sub"] == "user-123"
    assert payload["task_id"] == "task-123"
    assert payload["outcome"] == "success"
    assert payload["timezone"] == "UTC"


def test_mask_email_redacts_local_part() -> None:
    assert mask_email("alice@example.com") == "***@example.com"
    assert mask_email("no-at-sign") == "***"
