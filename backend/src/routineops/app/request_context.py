from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4


def new_request_id() -> str:
    return uuid4().hex


@dataclass(frozen=True)
class RequestContext:
    tenant_id: UUID
    user_sub: str
    auth_claims: dict[str, object] = field(default_factory=dict)
    request_id: str = field(default_factory=new_request_id)
