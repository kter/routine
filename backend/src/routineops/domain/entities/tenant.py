from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class Tenant:
    id: UUID
    name: str
    slug: str
    plan: str
    status: str
    settings: dict[str, object]
    created_at: datetime
    updated_at: datetime
