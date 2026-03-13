"""Unit tests for Cognito PostConfirmation Lambda trigger.

Mocked surfaces:
- boto3.client (dsql token generation + cognito admin_update_user_attributes)
- psycopg2.connect (DB connection / cursor)

The tests never touch a real DB or AWS service.
"""

import json
import os
import uuid
from unittest.mock import MagicMock, patch

import pytest

# Ensure required env var is set before importing the module
os.environ.setdefault("DB_CLUSTER_ENDPOINT", "test-cluster.dsql.ap-northeast-1.on.aws")
os.environ.setdefault("AWS_REGION", "ap-northeast-1")

from routineops.infrastructure.auth.post_confirmation_trigger import handler  # noqa: E402

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


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


def _make_mock_conn() -> MagicMock:
    """Create a mock psycopg2 connection with cursor as context manager."""
    mock_cursor = MagicMock()
    mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
    mock_cursor.__exit__ = MagicMock(return_value=False)

    mock_conn = MagicMock()
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)
    mock_conn.cursor.return_value = mock_cursor

    return mock_conn


def _patched_handler(event: dict, mock_conn: MagicMock, mock_cognito: MagicMock) -> dict:
    """Run handler with boto3 and psycopg2 fully mocked."""

    def fake_boto3_client(service_name: str, **kwargs):
        if service_name == "dsql":
            dsql = MagicMock()
            dsql.generate_db_connect_admin_auth_token.return_value = "fake-iam-token"
            return dsql
        if service_name == "cognito-idp":
            return mock_cognito
        raise ValueError(f"Unexpected boto3 service: {service_name}")

    with (
        patch(
            "routineops.infrastructure.auth.post_confirmation_trigger.boto3.client",
            side_effect=fake_boto3_client,
        ),
        patch(
            "routineops.infrastructure.auth.post_confirmation_trigger.psycopg2.connect",
            return_value=mock_conn,
        ),
    ):
        return handler(event, context=None)


# ---------------------------------------------------------------------------
# Test: trigger source filtering
# ---------------------------------------------------------------------------


class TestTriggerSourceFiltering:
    """Handler must be a no-op for any trigger other than PostConfirmation_ConfirmSignUp."""

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

        with (
            patch(
                "routineops.infrastructure.auth.post_confirmation_trigger.boto3.client"
            ) as mock_boto3,
            patch(
                "routineops.infrastructure.auth.post_confirmation_trigger.psycopg2.connect"
            ) as mock_psycopg2,
        ):
            result = handler(event, context=None)

        assert result is event
        mock_boto3.assert_not_called()
        mock_psycopg2.assert_not_called()


# ---------------------------------------------------------------------------
# Test: happy path
# ---------------------------------------------------------------------------


class TestHappyPath:
    def test_returns_original_event(self) -> None:
        event = _make_event()
        mock_conn = _make_mock_conn()
        mock_cognito = MagicMock()

        result = _patched_handler(event, mock_conn, mock_cognito)

        assert result is event

    def test_inserts_tenant_into_db(self) -> None:
        event = _make_event(email="alice@example.com")
        mock_conn = _make_mock_conn()
        mock_cognito = MagicMock()

        _patched_handler(event, mock_conn, mock_cognito)

        cursor = mock_conn.cursor.return_value.__enter__.return_value
        cursor.execute.assert_called_once()
        sql, params = cursor.execute.call_args.args
        tenant_id, name, slug, settings = params

        assert "INSERT INTO tenants" in sql
        assert name == "alice"
        assert slug == tenant_id  # slug is the UUID
        assert json.loads(settings) == {}

    def test_tenant_id_is_valid_uuid(self) -> None:
        event = _make_event()
        mock_conn = _make_mock_conn()
        mock_cognito = MagicMock()

        _patched_handler(event, mock_conn, mock_cognito)

        cursor = mock_conn.cursor.return_value.__enter__.return_value
        _, params = cursor.execute.call_args.args
        tenant_id = params[0]

        # Must not raise
        parsed = uuid.UUID(tenant_id)
        assert str(parsed) == tenant_id

    def test_sets_custom_tenant_id_in_cognito(self) -> None:
        event = _make_event(username="alice-sub", user_pool_id="ap-northeast-1_XYZ")
        mock_conn = _make_mock_conn()
        mock_cognito = MagicMock()

        _patched_handler(event, mock_conn, mock_cognito)

        cursor = mock_conn.cursor.return_value.__enter__.return_value
        _, params = cursor.execute.call_args.args
        expected_tenant_id = params[0]

        mock_cognito.admin_update_user_attributes.assert_called_once_with(
            UserPoolId="ap-northeast-1_XYZ",
            Username="alice-sub",
            UserAttributes=[{"Name": "custom:tenant_id", "Value": expected_tenant_id}],
        )

    def test_closes_db_connection(self) -> None:
        event = _make_event()
        mock_conn = _make_mock_conn()
        mock_cognito = MagicMock()

        _patched_handler(event, mock_conn, mock_cognito)

        mock_conn.close.assert_called_once()


# ---------------------------------------------------------------------------
# Test: email prefix extraction as tenant name
# ---------------------------------------------------------------------------


class TestNameExtraction:
    @pytest.mark.parametrize(
        "email, expected_name",
        [
            ("alice@example.com", "alice"),
            ("bob.smith+tag@company.co.jp", "bob.smith+tag"),
            ("admin@sub.domain.example.com", "admin"),
        ],
    )
    def test_extracts_email_prefix_as_name(self, email: str, expected_name: str) -> None:
        event = _make_event(email=email)
        mock_conn = _make_mock_conn()
        mock_cognito = MagicMock()

        _patched_handler(event, mock_conn, mock_cognito)

        cursor = mock_conn.cursor.return_value.__enter__.return_value
        _, params = cursor.execute.call_args.args
        _, name, *_ = params
        assert name == expected_name

    def test_uses_full_email_when_no_at_sign(self) -> None:
        """Handles malformed email gracefully — uses full string as name."""
        event = _make_event(email="noemail")
        mock_conn = _make_mock_conn()
        mock_cognito = MagicMock()

        _patched_handler(event, mock_conn, mock_cognito)

        cursor = mock_conn.cursor.return_value.__enter__.return_value
        _, params = cursor.execute.call_args.args
        _, name, *_ = params
        assert name == "noemail"


# ---------------------------------------------------------------------------
# Test: error handling
# ---------------------------------------------------------------------------


class TestErrorHandling:
    def test_db_failure_closes_connection_and_propagates(self) -> None:
        """If DB INSERT fails, the connection is still closed and exception propagates."""
        event = _make_event()

        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_cursor.execute.side_effect = RuntimeError("DB connection refused")

        mock_conn = MagicMock()
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)
        mock_conn.cursor.return_value = mock_cursor
        mock_cognito = MagicMock()

        with pytest.raises(RuntimeError, match="DB connection refused"):
            _patched_handler(event, mock_conn, mock_cognito)

        mock_conn.close.assert_called_once()

    def test_cognito_failure_propagates(self) -> None:
        """If AdminUpdateUserAttributes fails, the exception bubbles up."""
        event = _make_event()
        mock_conn = _make_mock_conn()
        mock_cognito = MagicMock()
        mock_cognito.admin_update_user_attributes.side_effect = RuntimeError("Cognito error")

        with pytest.raises(RuntimeError, match="Cognito error"):
            _patched_handler(event, mock_conn, mock_cognito)

    def test_cognito_not_called_if_db_fails(self) -> None:
        """Cognito attribute update should not be called when DB insert fails."""
        event = _make_event()

        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_cursor.execute.side_effect = RuntimeError("DB error")

        mock_conn = MagicMock()
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)
        mock_conn.cursor.return_value = mock_cursor
        mock_cognito = MagicMock()

        with pytest.raises(RuntimeError, match="DB error"):
            _patched_handler(event, mock_conn, mock_cognito)

        mock_cognito.admin_update_user_attributes.assert_not_called()

    def test_missing_db_cluster_endpoint_raises(self) -> None:
        """Handler must fail fast if DB_CLUSTER_ENDPOINT is not configured."""
        event = _make_event()

        with patch.dict(os.environ, {}, clear=False):
            saved = os.environ.pop("DB_CLUSTER_ENDPOINT", None)
            try:
                with pytest.raises(ValueError, match="DB_CLUSTER_ENDPOINT is not configured"):
                    handler(event, context=None)
            finally:
                if saved is not None:
                    os.environ["DB_CLUSTER_ENDPOINT"] = saved


# ---------------------------------------------------------------------------
# Test: IAM token is used as DB password
# ---------------------------------------------------------------------------


class TestIamTokenAuthentication:
    def test_connect_uses_iam_token_as_password(self) -> None:
        event = _make_event()
        mock_conn = _make_mock_conn()
        mock_cognito = MagicMock()

        mock_dsql = MagicMock()
        mock_dsql.generate_db_connect_admin_auth_token.return_value = "my-iam-token"

        def fake_boto3_client(service_name: str, **kwargs):
            if service_name == "dsql":
                return mock_dsql
            return mock_cognito

        with (
            patch(
                "routineops.infrastructure.auth.post_confirmation_trigger.boto3.client",
                side_effect=fake_boto3_client,
            ),
            patch(
                "routineops.infrastructure.auth.post_confirmation_trigger.psycopg2.connect",
                return_value=mock_conn,
            ) as mock_connect,
        ):
            handler(event, context=None)

        call_kwargs = mock_connect.call_args.kwargs
        assert call_kwargs["password"] == "my-iam-token"
        assert call_kwargs["user"] == "admin"
        assert call_kwargs["sslmode"] == "require"
