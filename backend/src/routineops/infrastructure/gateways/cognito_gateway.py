from __future__ import annotations

import boto3


class CognitoGateway:
    def __init__(self, region: str) -> None:
        self._client = boto3.client("cognito-idp", region_name=region)

    def set_tenant_id(self, user_pool_id: str, username: str, tenant_id: str) -> None:
        self._client.admin_update_user_attributes(
            UserPoolId=user_pool_id,
            Username=username,
            UserAttributes=[
                {"Name": "custom:tenant_id", "Value": tenant_id},
            ],
        )
