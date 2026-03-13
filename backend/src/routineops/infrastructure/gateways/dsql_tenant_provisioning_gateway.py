from __future__ import annotations

import json

import boto3
import psycopg2


class DsqlTenantProvisioningGateway:
    def __init__(self, cluster_endpoint: str, region: str, db_name: str) -> None:
        self._cluster_endpoint = cluster_endpoint
        self._region = region
        self._db_name = db_name

    def create_tenant(self, tenant_id: str, name: str, slug: str) -> None:
        conn = self._get_db_connection()
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
        finally:
            conn.close()

    def _get_db_connection(self) -> psycopg2.extensions.connection:
        token = self._get_dsql_token()
        return psycopg2.connect(
            host=self._cluster_endpoint,
            port=5432,
            user="admin",
            password=token,
            dbname=self._db_name,
            sslmode="require",
        )

    def _get_dsql_token(self) -> str:
        client = boto3.client("dsql", region_name=self._region)
        token: str = client.generate_db_connect_admin_auth_token(
            Hostname=self._cluster_endpoint,
            Region=self._region,
        )
        return token
