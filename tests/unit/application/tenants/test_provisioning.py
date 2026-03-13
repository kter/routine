from __future__ import annotations

from unittest.mock import MagicMock, patch

from routineops.application.tenants.provisioning import (
    ProvisionTenantService,
    SignupUser,
)


def test_provision_for_signup_creates_tenant_and_sets_attribute() -> None:
    tenant_gateway = MagicMock()
    user_attribute_gateway = MagicMock()
    service = ProvisionTenantService(tenant_gateway, user_attribute_gateway)
    user = SignupUser(
        email="alice@example.com",
        user_pool_id="pool-id",
        username="alice-sub",
    )

    with patch(
        "routineops.application.tenants.provisioning.uuid4",
        return_value="tenant-123",
    ):
        tenant_id = service.provision_for_signup(user)

    assert tenant_id == "tenant-123"
    tenant_gateway.create_tenant.assert_called_once_with(
        tenant_id="tenant-123",
        name="alice",
        slug="tenant-123",
    )
    user_attribute_gateway.set_tenant_id.assert_called_once_with(
        user_pool_id="pool-id",
        username="alice-sub",
        tenant_id="tenant-123",
    )


def test_provision_for_signup_uses_full_email_when_missing_at_sign() -> None:
    tenant_gateway = MagicMock()
    user_attribute_gateway = MagicMock()
    service = ProvisionTenantService(tenant_gateway, user_attribute_gateway)

    with patch(
        "routineops.application.tenants.provisioning.uuid4",
        return_value="tenant-456",
    ):
        service.provision_for_signup(
            SignupUser(
                email="noemail",
                user_pool_id="pool-id",
                username="user-sub",
            )
        )

    tenant_gateway.create_tenant.assert_called_once_with(
        tenant_id="tenant-456",
        name="noemail",
        slug="tenant-456",
    )
