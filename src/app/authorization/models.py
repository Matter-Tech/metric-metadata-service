from datetime import datetime
from uuid import UUID

from matter_persistence.foundation_model import FoundationModel


class IdentityModel(FoundationModel):
    id: UUID
    client_id: str
    last_time_used: datetime
    organization_id: UUID
