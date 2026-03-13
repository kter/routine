from __future__ import annotations

from unittest.mock import MagicMock, patch

from routineops.infrastructure.gateways.cognito_gateway import CognitoGateway


def test_set_tenant_id_updates_custom_attribute() -> None:
    client = MagicMock()

    with patch(
        "routineops.infrastructure.gateways.cognito_gateway.boto3.client",
        return_value=client,
    ):
        gateway = CognitoGateway(region="ap-northeast-1")

    gateway.set_tenant_id("pool-id", "alice-sub", "tenant-123")

    client.admin_update_user_attributes.assert_called_once_with(
        UserPoolId="pool-id",
        Username="alice-sub",
        UserAttributes=[{"Name": "custom:tenant_id", "Value": "tenant-123"}],
    )
