import logging
import os
from collections.abc import Mapping
from functools import lru_cache
from typing import Any

import boto3
import sentry_sdk
from botocore.exceptions import BotoCoreError, ClientError
from sentry_sdk.integrations.aws_lambda import AwsLambdaIntegration
from sentry_sdk.integrations.fastapi import FastApiIntegration

DEFAULT_TRACES_SAMPLE_RATE = 0.1
DEFAULT_AWS_REGION = "ap-northeast-1"

logger = logging.getLogger(__name__)


def _parse_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default

    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False

    return default


def _parse_sample_rate(value: str | None) -> float:
    if value is None:
        return DEFAULT_TRACES_SAMPLE_RATE

    try:
        sample_rate = float(value)
    except ValueError:
        return DEFAULT_TRACES_SAMPLE_RATE

    if 0 <= sample_rate <= 1:
        return sample_rate

    return DEFAULT_TRACES_SAMPLE_RATE


@lru_cache(maxsize=8)
def _get_secure_parameter(parameter_name: str, region: str) -> str | None:
    try:
        client = boto3.client("ssm", region_name=region)
        response = client.get_parameter(Name=parameter_name, WithDecryption=True)
    except (BotoCoreError, ClientError):
        logger.exception("Failed to load Sentry DSN from SSM parameter %s", parameter_name)
        return None

    value = response["Parameter"]["Value"].strip()
    return value or None


def _resolve_sentry_dsn(env: Mapping[str, str]) -> str | None:
    direct_dsn = env.get("SENTRY_DSN", "").strip()
    if direct_dsn:
        return direct_dsn

    parameter_name = env.get("SENTRY_DSN_PARAMETER_NAME", "").strip()
    if not parameter_name:
        return None

    region = env.get("AWS_REGION", env.get("AWS_DEFAULT_REGION", DEFAULT_AWS_REGION))
    return _get_secure_parameter(parameter_name, region)


def get_sentry_init_kwargs(
    env: Mapping[str, str],
    *,
    include_fastapi: bool,
) -> dict[str, Any] | None:
    dsn = _resolve_sentry_dsn(env)
    if not dsn:
        return None

    integrations: list[Any] = [AwsLambdaIntegration(timeout_warning=True)]
    if include_fastapi:
        integrations.append(FastApiIntegration())

    return {
        "dsn": dsn,
        "environment": env.get("SENTRY_ENVIRONMENT", env.get("ENV", "development")),
        "integrations": integrations,
        "send_default_pii": _parse_bool(env.get("SENTRY_SEND_DEFAULT_PII"), default=True),
        "traces_sample_rate": _parse_sample_rate(env.get("SENTRY_TRACES_SAMPLE_RATE")),
    }


def init_sentry(*, include_fastapi: bool) -> bool:
    kwargs = get_sentry_init_kwargs(os.environ, include_fastapi=include_fastapi)
    if kwargs is None:
        return False

    sentry_sdk.init(**kwargs)
    return True
