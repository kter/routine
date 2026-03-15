from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol
from uuid import uuid4


@dataclass(frozen=True)
class SignupUser:
    email: str
    user_pool_id: str
    username: str


class TenantProvisioningGateway(Protocol):
    def create_tenant(self, tenant_id: str, name: str, slug: str) -> None: ...


class UserAttributeGateway(Protocol):
    def set_tenant_id(self, user_pool_id: str, username: str, tenant_id: str) -> None: ...


class ProvisionTenantService:
    def __init__(
        self,
        tenant_gateway: TenantProvisioningGateway,
        user_attribute_gateway: UserAttributeGateway,
    ) -> None:
        self._tenant_gateway = tenant_gateway
        self._user_attribute_gateway = user_attribute_gateway

    def provision_for_signup(self, user: SignupUser) -> str:
        tenant_id = str(uuid4())
        name = _derive_tenant_name(user.email)
        slug = tenant_id

        self._tenant_gateway.create_tenant(
            tenant_id=tenant_id,
            name=name,
            slug=slug,
        )
        self._user_attribute_gateway.set_tenant_id(
            user_pool_id=user.user_pool_id,
            username=user.username,
            tenant_id=tenant_id,
        )
        return tenant_id


def _derive_tenant_name(email: str) -> str:
    return email.split("@")[0] if "@" in email else email
