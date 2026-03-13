from __future__ import annotations

from routineops.application.tenants.provisioning import ProvisionTenantService
from routineops.config.settings import TenantProvisioningSettings
from routineops.infrastructure.gateways.cognito_gateway import CognitoGateway
from routineops.infrastructure.gateways.dsql_tenant_provisioning_gateway import (
    DsqlTenantProvisioningGateway,
)


def build_tenant_provisioning_service(
    settings: TenantProvisioningSettings,
) -> ProvisionTenantService:
    if not settings.db_cluster_endpoint:
        raise ValueError("DB_CLUSTER_ENDPOINT is not configured")

    return ProvisionTenantService(
        tenant_gateway=DsqlTenantProvisioningGateway(
            cluster_endpoint=settings.db_cluster_endpoint,
            region=settings.aws_region,
            db_name=settings.db_name,
        ),
        user_attribute_gateway=CognitoGateway(region=settings.aws_region),
    )
