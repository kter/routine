from __future__ import annotations

import boto3

from routineops.app.auth import TENANT_ID_CLAIM


class CognitoGateway:
    def __init__(self, region: str) -> None:
        self._client = boto3.client("cognito-idp", region_name=region)

    def set_tenant_id(self, user_pool_id: str, username: str, tenant_id: str) -> None:
        self._client.admin_update_user_attributes(
            UserPoolId=user_pool_id,
            Username=username,
            UserAttributes=[
                {"Name": TENANT_ID_CLAIM, "Value": tenant_id},
            ],
        )
