import uuid
from datetime import datetime, timezone
from typing import List

from matter_persistence.foundation_model import FoundationModel
from pydantic import BaseModel, Field

from app.common.enums.enums import EntityTypeEnum, EventTypeEnum


class EventFilterInDTO(BaseModel):
    event_type: EventTypeEnum | None = Field(None, alias="eventType")
    node_type: EntityTypeEnum | None = Field(None, alias="nodeType")
    node_id: uuid.UUID | None = Field(None, alias="nodeId")
    user_id: uuid.UUID | None = Field(None, alias="userId")


class EventOutDTO(FoundationModel):
    id: uuid.UUID


class FullEventOutDTO(EventOutDTO):
    event_type: EventTypeEnum | None = Field(None, alias="eventType")
    node_type: EntityTypeEnum | None = Field(None, alias="nodeType")
    node_id: uuid.UUID | None = Field(None, alias="nodeId")
    user_id: uuid.UUID | None = Field(None, alias="userId")
    created: datetime | None = Field(None, alias="timestamp")
    new_data: dict | None = Field(None, alias="newData")


class EventDeletionOutDTO(EventOutDTO):
    deleted_at: datetime = Field(datetime.now(tz=timezone.utc), alias="deletedAt")


class EventListOutDTO(FoundationModel):
    count: int
    events: List[FullEventOutDTO]
