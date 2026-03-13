"""
Cognito PostConfirmation Lambda trigger.
Creates a tenant in the DB and sets the custom:tenant_id attribute on the user.
"""

import json
import logging
import uuid

import boto3
import psycopg2

from routineops.config.settings import get_post_confirmation_settings
from routineops.infrastructure.monitoring.sentry import init_sentry

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

init_sentry(include_fastapi=False)


def _get_dsql_token(hostname: str, region: str) -> str:
    client = boto3.client("dsql", region_name=region)
    token: str = client.generate_db_connect_admin_auth_token(
        Hostname=hostname,
        Region=region,
    )
    return token


def _get_db_connection(cluster_endpoint: str, region: str) -> psycopg2.extensions.connection:
    token = _get_dsql_token(cluster_endpoint, region)
    settings = get_post_confirmation_settings()
    conn = psycopg2.connect(
        host=cluster_endpoint,
        port=5432,
        user="admin",
        password=token,
        dbname=settings.db_name,
        sslmode="require",
    )
    return conn


def handler(event: dict, context: object) -> dict:
    trigger_source = event.get("triggerSource", "")
    if trigger_source != "PostConfirmation_ConfirmSignUp":
        return event

    user_attributes = event.get("request", {}).get("userAttributes", {})
    email: str = user_attributes.get("email", "")
    user_pool_id: str = event.get("userPoolId", "")
    username: str = event.get("userName", "")

    settings = get_post_confirmation_settings()
    if not settings.db_cluster_endpoint:
        raise ValueError("DB_CLUSTER_ENDPOINT is not configured")

    tenant_id = str(uuid.uuid4())
    # Use email prefix as name, UUID as slug (unique, URL-safe)
    name = email.split("@")[0] if "@" in email else email
    slug = tenant_id

    logger.info("Creating tenant for user %s, email %s", username, email)

    conn = _get_db_connection(settings.db_cluster_endpoint, settings.aws_region)
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO tenants (id, name, slug, plan, status, settings)
                    VALUES (%s, %s, %s, 'free', 'active', %s)
                    """,
                    (tenant_id, name, slug, json.dumps({})),
                )
        logger.info("Inserted tenant %s", tenant_id)
    finally:
        conn.close()

    cognito = boto3.client("cognito-idp", region_name=settings.aws_region)
    cognito.admin_update_user_attributes(
        UserPoolId=user_pool_id,
        Username=username,
        UserAttributes=[
            {"Name": "custom:tenant_id", "Value": tenant_id},
        ],
    )
    logger.info("Set custom:tenant_id=%s for user %s", tenant_id, username)

    return event
