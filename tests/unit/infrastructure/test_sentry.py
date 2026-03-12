from sentry_sdk.integrations.aws_lambda import AwsLambdaIntegration
from sentry_sdk.integrations.fastapi import FastApiIntegration

from routineops.infrastructure.monitoring.sentry import get_sentry_init_kwargs


def test_get_sentry_init_kwargs_returns_none_without_dsn() -> None:
    assert get_sentry_init_kwargs({}, include_fastapi=True) is None


def test_get_sentry_init_kwargs_for_fastapi_lambda() -> None:
    kwargs = get_sentry_init_kwargs(
        {
            "ENV": "dev",
            "SENTRY_DSN": "https://examplePublicKey@o0.ingest.sentry.io/0",
            "SENTRY_TRACES_SAMPLE_RATE": "0.25",
            "SENTRY_SEND_DEFAULT_PII": "false",
        },
        include_fastapi=True,
    )

    assert kwargs is not None
    assert kwargs["dsn"] == "https://examplePublicKey@o0.ingest.sentry.io/0"
    assert kwargs["environment"] == "dev"
    assert kwargs["send_default_pii"] is False
    assert kwargs["traces_sample_rate"] == 0.25
    assert any(
        isinstance(integration, AwsLambdaIntegration) for integration in kwargs["integrations"]
    )
    assert any(
        isinstance(integration, FastApiIntegration) for integration in kwargs["integrations"]
    )

    aws_integration = next(
        integration
        for integration in kwargs["integrations"]
        if isinstance(integration, AwsLambdaIntegration)
    )
    assert aws_integration.timeout_warning is True


def test_get_sentry_init_kwargs_defaults_invalid_values() -> None:
    kwargs = get_sentry_init_kwargs(
        {
            "SENTRY_DSN": "https://examplePublicKey@o0.ingest.sentry.io/0",
            "SENTRY_SEND_DEFAULT_PII": "not-a-bool",
            "SENTRY_TRACES_SAMPLE_RATE": "2.5",
        },
        include_fastapi=False,
    )

    assert kwargs is not None
    assert kwargs["environment"] == "development"
    assert kwargs["send_default_pii"] is True
    assert kwargs["traces_sample_rate"] == 0.1
    assert len(kwargs["integrations"]) == 1
    assert isinstance(kwargs["integrations"][0], AwsLambdaIntegration)
