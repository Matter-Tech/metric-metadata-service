import json
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

_SUPERUSER_PERMISSION_SCOPE = "platform:superuser:read"


class AuthorizedClient(BaseModel):
    """
    Authorized client information.

    Holds data from client and client_metadata tables.
    """

    user_id: UUID
    organization_id: UUID
    permissions: list[str] = []
    created_at: datetime | None = None
    metadata: dict | None = None

    def is_super_user(self) -> bool:
        return _SUPERUSER_PERMISSION_SCOPE in self.permissions

    def __eq__(self, other):
        return all(
            [
                self.user_id == other.user_id,
                self.organization_id == other.organization_id,
                self.created_at == other.created_at,
                self.permissions == other.permissions,
            ]
        )

    def __repr__(self):
        return f"Client: {self.user_id}::{self.organization_id}"

    @property
    def to_matter_auth(self):
        return {
            "x-matter-user-id": str(self.user_id),
            "x-matter-org-id": str(self.organization_id),
            "x-matter-permissions": json.dumps(self.permissions),
        }
