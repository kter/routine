from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from routineops.application.tenants.bootstrap import build_tenant_provisioning_service
from routineops.application.tenants.provisioning import ProvisionTenantService


def test_build_tenant_provisioning_service_raises_without_db_endpoint() -> None:
    settings = SimpleNamespace(
        db_cluster_endpoint=None,
        aws_region="ap-northeast-1",
        db_name="postgres",
    )

    with pytest.raises(ValueError, match="DB_CLUSTER_ENDPOINT is not configured"):
        build_tenant_provisioning_service(settings)


def test_build_tenant_provisioning_service_wires_gateways() -> None:
    settings = SimpleNamespace(
        db_cluster_endpoint="cluster.example",
        aws_region="ap-northeast-1",
        db_name="postgres",
    )
    tenant_gateway = MagicMock()
    user_attribute_gateway = MagicMock()

    with (
        patch(
            "routineops.application.tenants.bootstrap.DsqlTenantProvisioningGateway",
            return_value=tenant_gateway,
        ) as tenant_gateway_cls,
        patch(
            "routineops.application.tenants.bootstrap.CognitoGateway",
            return_value=user_attribute_gateway,
        ) as user_attribute_gateway_cls,
    ):
        service = build_tenant_provisioning_service(settings)

    assert isinstance(service, ProvisionTenantService)
    tenant_gateway_cls.assert_called_once_with(
        cluster_endpoint="cluster.example",
        region="ap-northeast-1",
        db_name="postgres",
    )
    user_attribute_gateway_cls.assert_called_once_with(region="ap-northeast-1")
