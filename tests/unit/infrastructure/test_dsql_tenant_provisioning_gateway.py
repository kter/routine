from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from routineops.infrastructure.gateways.dsql_tenant_provisioning_gateway import (
    DsqlTenantProvisioningGateway,
)


def _make_mock_conn() -> MagicMock:
    mock_cursor = MagicMock()
    mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
    mock_cursor.__exit__ = MagicMock(return_value=False)

    mock_conn = MagicMock()
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)
    mock_conn.cursor.return_value = mock_cursor

    return mock_conn


def test_create_tenant_inserts_expected_record_and_closes_connection() -> None:
    mock_conn = _make_mock_conn()
    mock_dsql = MagicMock()
    mock_dsql.generate_db_connect_admin_auth_token.return_value = "fake-token"

    with (
        patch(
            "routineops.infrastructure.gateways.dsql_tenant_provisioning_gateway.boto3.client",
            return_value=mock_dsql,
        ),
        patch(
            "routineops.infrastructure.gateways.dsql_tenant_provisioning_gateway.psycopg2.connect",
            return_value=mock_conn,
        ) as connect,
    ):
        gateway = DsqlTenantProvisioningGateway(
            cluster_endpoint="cluster.example",
            region="ap-northeast-1",
            db_name="postgres",
        )
        gateway.create_tenant("tenant-123", "alice", "tenant-123")

    call_kwargs = connect.call_args.kwargs
    assert call_kwargs["password"] == "fake-token"
    assert call_kwargs["dbname"] == "postgres"
    assert call_kwargs["sslmode"] == "require"

    cursor = mock_conn.cursor.return_value.__enter__.return_value
    sql, params = cursor.execute.call_args.args
    tenant_id, name, slug, settings = params

    assert "INSERT INTO tenants" in sql
    assert tenant_id == "tenant-123"
    assert name == "alice"
    assert slug == "tenant-123"
    assert json.loads(settings) == {}
    mock_conn.close.assert_called_once()
