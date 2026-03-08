"""
Cognito PostConfirmation Lambda trigger.
Creates a tenant in the DB and sets the custom:tenant_id attribute on the user.
"""

import json
import logging
import os
import uuid

import boto3
import psycopg2

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def _get_dsql_token(hostname: str, region: str) -> str:
    client = boto3.client("dsql", region_name=region)
    token: str = client.generate_db_connect_admin_auth_token(
        Hostname=hostname,
        Region=region,
    )
    return token


def _get_db_connection(cluster_endpoint: str, region: str) -> psycopg2.extensions.connection:
    token = _get_dsql_token(cluster_endpoint, region)
    conn = psycopg2.connect(
        host=cluster_endpoint,
        port=5432,
        user="admin",
        password=token,
        dbname="routineops",
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

    cluster_endpoint = os.environ["DB_CLUSTER_ENDPOINT"]
    region = os.environ.get("AWS_REGION", "ap-northeast-1")

    tenant_id = str(uuid.uuid4())
    # Use email prefix as name, UUID as slug (unique, URL-safe)
    name = email.split("@")[0] if "@" in email else email
    slug = tenant_id

    logger.info("Creating tenant for user %s, email %s", username, email)

    conn = _get_db_connection(cluster_endpoint, region)
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

    cognito = boto3.client("cognito-idp", region_name=region)
    cognito.admin_update_user_attributes(
        UserPoolId=user_pool_id,
        Username=username,
        UserAttributes=[
            {"Name": "custom:tenant_id", "Value": tenant_id},
        ],
    )
    logger.info("Set custom:tenant_id=%s for user %s", tenant_id, username)

    return event
