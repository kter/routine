"""Unit tests for the Cognito PostConfirmation Lambda trigger."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from routineops.application.tenants.provisioning import SignupUser
from routineops.infrastructure.auth.post_confirmation_trigger import handler


def _make_event(
    trigger_source: str = "PostConfirmation_ConfirmSignUp",
    email: str = "alice@example.com",
    username: str = "alice-user-sub",
    user_pool_id: str = "ap-northeast-1_TestPool",
) -> dict:
    return {
        "triggerSource": trigger_source,
        "userPoolId": user_pool_id,
        "userName": username,
        "request": {
            "userAttributes": {
                "email": email,
                "sub": username,
            }
        },
        "response": {},
    }


class TestTriggerSourceFiltering:
    @pytest.mark.parametrize(
        "trigger_source",
        [
            "PostConfirmation_ConfirmForgotPassword",
            "PreSignUp_SignUp",
            "PostAuthentication_Authentication",
            "",
            "unknown",
        ],
    )
    def test_returns_event_unchanged_for_other_triggers(self, trigger_source: str) -> None:
        event = _make_event(trigger_source=trigger_source)

        with patch(
            "routineops.infrastructure.auth.post_confirmation_trigger.build_tenant_provisioning_service"
        ) as build_service:
            result = handler(event, context=None)

        assert result is event
        build_service.assert_not_called()


def test_provisions_tenant_for_signup_user() -> None:
    event = _make_event(username="alice-sub", user_pool_id="pool-id")
    service = MagicMock()
    service.provision_for_signup.return_value = "tenant-123"
    settings = SimpleNamespace(
        db_cluster_endpoint="cluster.example",
        aws_region="ap-northeast-1",
        db_name="postgres",
    )

    with (
        patch(
            "routineops.infrastructure.auth.post_confirmation_trigger.get_tenant_provisioning_settings",
            return_value=settings,
        ),
        patch(
            "routineops.infrastructure.auth.post_confirmation_trigger.build_tenant_provisioning_service",
            return_value=service,
        ) as build_service,
    ):
        result = handler(event, context=None)

    assert result is event
    build_service.assert_called_once_with(settings)
    service.provision_for_signup.assert_called_once_with(
        SignupUser(
            email="alice@example.com",
            user_pool_id="pool-id",
            username="alice-sub",
        )
    )


def test_missing_db_cluster_endpoint_raises() -> None:
    event = _make_event()
    settings = SimpleNamespace(
        db_cluster_endpoint=None,
        aws_region="ap-northeast-1",
        db_name="postgres",
    )

    with patch(
        "routineops.infrastructure.auth.post_confirmation_trigger.get_tenant_provisioning_settings",
        return_value=settings,
    ):
        with pytest.raises(ValueError, match="DB_CLUSTER_ENDPOINT is not configured"):
            handler(event, context=None)
