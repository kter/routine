"""Cognito PostConfirmation Lambda trigger."""

import logging

from routineops.application.tenants import (
    SignupUser,
    build_tenant_provisioning_service,
)
from routineops.config.settings import get_tenant_provisioning_settings
from routineops.infrastructure.monitoring.logging import (
    bind_log_context,
    configure_logging,
    emit_structured_log,
    mask_email,
    reset_log_context,
    set_sentry_request_context,
)
from routineops.infrastructure.monitoring.sentry import init_sentry

logger = logging.getLogger(__name__)

settings = get_tenant_provisioning_settings()
configure_logging(
    level=settings.log_level,
    log_format=settings.log_format,
    environment=settings.env,
    component="post_confirmation",
)
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
    aws_request_id = getattr(context, "aws_request_id", None)
    context_token = bind_log_context(aws_request_id=aws_request_id)
    set_sentry_request_context(component="post_confirmation", aws_request_id=aws_request_id)

    try:
        settings = get_tenant_provisioning_settings()
        emit_structured_log(
            logger,
            logging.INFO,
            "Tenant provisioning started for confirmed signup",
            event_name="tenant_provisioning_started",
            username=username,
            email=mask_email(email),
            user_pool_id=user_pool_id,
            outcome="success",
        )
        service = build_tenant_provisioning_service(settings)
        tenant_id = service.provision_for_signup(
            SignupUser(
                email=email,
                user_pool_id=user_pool_id,
                username=username,
            )
        )
        emit_structured_log(
            logger,
            logging.INFO,
            "Tenant provisioning completed",
            event_name="tenant_provisioning_completed",
            username=username,
            tenant_id=tenant_id,
            outcome="success",
        )
        return event
    except Exception:
        logger.exception(
            "Tenant provisioning failed",
            extra={
                "event_name": "tenant_provisioning_failed",
                "username": username,
                "email": mask_email(email),
                "user_pool_id": user_pool_id,
                "outcome": "error",
            },
        )
        raise
    finally:
        reset_log_context(context_token)
