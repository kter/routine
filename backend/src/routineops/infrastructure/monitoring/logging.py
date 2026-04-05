from __future__ import annotations

import json
import logging
import sys
from contextvars import ContextVar, Token
from datetime import UTC, datetime

import sentry_sdk

DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_LOG_FORMAT = "json"
DEFAULT_SERVICE_NAME = "routineops"
UTC_TIMEZONE_NAME = "UTC"
_LOG_CONTEXT: ContextVar[dict[str, object] | None] = ContextVar(
    "routineops_log_context",
    default=None,
)
_ROOT_LOG_RECORD_FIELDS = frozenset(vars(logging.makeLogRecord({})))
_CONFIG_SIGNATURE: tuple[str, str, str, str] | None = None


def _sanitize_value(value: object) -> object:
    if isinstance(value, dict):
        return {key: _sanitize_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_sanitize_value(item) for item in value]
    return value


def _merge_extra_fields(record: logging.LogRecord) -> dict[str, object]:
    fields: dict[str, object] = {}
    for key, value in record.__dict__.items():
        if key in _ROOT_LOG_RECORD_FIELDS or key.startswith("_"):
            continue
        fields[key] = _sanitize_value(value)
    return fields


class JsonFormatter(logging.Formatter):
    def __init__(
        self,
        *,
        environment: str,
        component: str,
        service: str = DEFAULT_SERVICE_NAME,
    ) -> None:
        super().__init__()
        self._environment = environment
        self._component = component
        self._service = service

    def format(self, record: logging.LogRecord) -> str:
        context = get_log_context()
        extra_fields = _merge_extra_fields(record)

        payload: dict[str, object] = {
            "timestamp": datetime.now(tz=UTC).isoformat(),
            "timezone": UTC_TIMEZONE_NAME,
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "event_name": extra_fields.pop("event_name", "log"),
            "service": self._service,
            "environment": self._environment,
            "component": extra_fields.pop("component", self._component),
            "request_id": context.get("request_id"),
            "tenant_id": context.get("tenant_id"),
            "user_sub": context.get("user_sub"),
            "aws_request_id": context.get("aws_request_id"),
            "outcome": extra_fields.get("outcome"),
        }

        for source in (context, extra_fields):
            for key, value in source.items():
                if value is None:
                    continue
                payload[key] = value

        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)

        return json.dumps(payload, default=str, ensure_ascii=True)


def bind_log_context(**fields: object) -> Token[dict[str, object] | None]:
    context = get_log_context()
    for key, value in fields.items():
        if value is not None:
            context[key] = value
    return _LOG_CONTEXT.set(context)


def reset_log_context(token: Token[dict[str, object] | None]) -> None:
    _LOG_CONTEXT.reset(token)


def clear_log_context() -> None:
    _LOG_CONTEXT.set({})


def get_log_context() -> dict[str, object]:
    context = _LOG_CONTEXT.get()
    return {} if context is None else dict(context)


def emit_structured_log(
    logger: logging.Logger,
    level: int,
    message: str,
    *,
    event_name: str,
    **fields: object,
) -> None:
    context = get_log_context()
    logger.log(level, message, extra={**context, "event_name": event_name, **fields})


def configure_logging(
    *,
    level: str,
    log_format: str,
    environment: str,
    component: str,
) -> None:
    global _CONFIG_SIGNATURE

    normalized_level = (level or DEFAULT_LOG_LEVEL).upper()
    normalized_format = (log_format or DEFAULT_LOG_FORMAT).lower()
    signature = (normalized_level, normalized_format, environment, component)
    if _CONFIG_SIGNATURE == signature:
        return

    handler = logging.StreamHandler(sys.stdout)
    if normalized_format == "plain":
        handler.setFormatter(
            logging.Formatter(
                fmt="%(asctime)s %(levelname)s [%(name)s] %(message)s",
                datefmt="%Y-%m-%dT%H:%M:%S%z",
            )
        )
    else:
        handler.setFormatter(
            JsonFormatter(
                environment=environment,
                component=component,
            )
        )

    root_logger = logging.getLogger()
    root_logger.handlers = [handler]
    root_logger.setLevel(getattr(logging, normalized_level, logging.INFO))

    for noisy_logger in (
        "alembic",
        "boto3",
        "botocore",
        "sqlalchemy.engine",
        "s3transfer",
        "urllib3",
    ):
        logging.getLogger(noisy_logger).setLevel(logging.WARNING)

    _CONFIG_SIGNATURE = signature


def mask_email(email: str) -> str:
    normalized = email.strip()
    if "@" not in normalized:
        return "***"

    _, domain = normalized.split("@", 1)
    return f"***@{domain}"


def set_sentry_request_context(
    *,
    request_id: str | None = None,
    tenant_id: object | None = None,
    user_sub: str | None = None,
    component: str | None = None,
    aws_request_id: str | None = None,
) -> None:
    if request_id:
        sentry_sdk.set_tag("request_id", request_id)
    if tenant_id is not None:
        sentry_sdk.set_tag("tenant_id", str(tenant_id))
    if component:
        sentry_sdk.set_tag("component", component)
    if aws_request_id:
        sentry_sdk.set_tag("aws_request_id", aws_request_id)
    if user_sub or tenant_id is not None:
        sentry_sdk.set_user(
            {
                "id": user_sub or "",
                "tenant_id": None if tenant_id is None else str(tenant_id),
            }
        )


def clear_sentry_request_context() -> None:
    sentry_sdk.set_user(None)
