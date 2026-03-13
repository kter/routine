"""Cognito PostConfirmation Lambda trigger."""

import logging

from routineops.application.services.provision_tenant_service import (
    ProvisionTenantService,
    SignupUser,
)
from routineops.config.settings import PostConfirmationSettings, get_post_confirmation_settings
from routineops.infrastructure.gateways.cognito_gateway import CognitoGateway
from routineops.infrastructure.gateways.dsql_tenant_provisioning_gateway import (
    DsqlTenantProvisioningGateway,
)
from routineops.infrastructure.monitoring.sentry import init_sentry

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

init_sentry(include_fastapi=False)


def _build_service(settings: PostConfirmationSettings) -> ProvisionTenantService:
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


def handler(event: dict, context: object) -> dict:
    trigger_source = event.get("triggerSource", "")
    if trigger_source != "PostConfirmation_ConfirmSignUp":
        return event

    user_attributes = event.get("request", {}).get("userAttributes", {})
    email: str = user_attributes.get("email", "")
    user_pool_id: str = event.get("userPoolId", "")
    username: str = event.get("userName", "")

    settings = get_post_confirmation_settings()
    logger.info("Creating tenant for user %s, email %s", username, email)
    service = _build_service(settings)
    tenant_id = service.provision_for_signup(
        SignupUser(
            email=email,
            user_pool_id=user_pool_id,
            username=username,
        )
    )
    logger.info("Provisioned tenant %s for user %s", tenant_id, username)

    return event
