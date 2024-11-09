from matter_persistence.sql.base import CustomBase
from sqlalchemy import UUID, Column, DateTime, Enum
from sqlalchemy.dialects.postgresql import JSONB

from app.common.enums.enums import EntityTypeEnum, EventTypeEnum


class EventModel(CustomBase):
    __tablename__ = "events"

    event_type = Column(Enum(EventTypeEnum), nullable=False)
    node_type = Column(Enum(EntityTypeEnum), index=True, nullable=False)
    node_id = Column(UUID(as_uuid=True), index=True, nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=True)
    new_data = Column(JSONB, nullable=True)
