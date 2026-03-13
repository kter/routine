"""Cognito PostConfirmation Lambda trigger."""

import logging

from routineops.application.tenants import (
    SignupUser,
    build_tenant_provisioning_service,
)
from routineops.config.settings import get_tenant_provisioning_settings
from routineops.infrastructure.monitoring.sentry import init_sentry

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

init_sentry(include_fastapi=False)


def handler(event: dict[str, object], context: object) -> dict[str, object]:
    trigger_source = event.get("triggerSource", "")
    if trigger_source != "PostConfirmation_ConfirmSignUp":
        return event

    request_data = event.get("request", {})
    if not isinstance(request_data, dict):
        request_data = {}
    user_attributes = request_data.get("userAttributes", {})
    if not isinstance(user_attributes, dict):
        user_attributes = {}
    email = str(user_attributes.get("email", ""))
    user_pool_id = str(event.get("userPoolId", ""))
    username = str(event.get("userName", ""))

    settings = get_tenant_provisioning_settings()
    logger.info("Creating tenant for user %s, email %s", username, email)
    service = build_tenant_provisioning_service(settings)
    tenant_id = service.provision_for_signup(
        SignupUser(
            email=email,
            user_pool_id=user_pool_id,
            username=username,
        )
    )
    logger.info("Provisioned tenant %s for user %s", tenant_id, username)

    return event
