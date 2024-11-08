from matter_persistence.sql.base import CustomBase
from sqlalchemy import JSON, UUID, Column, DateTime, Enum

from app.common.enums.enums import EntityTypeEnum, EventTypeEnum


class EventModel(CustomBase):
    __tablename__ = "events"

    event_type = Column(Enum(EventTypeEnum), nullable=False)
    node_type = Column(Enum(EntityTypeEnum), nullable=False)
    node_id = Column(UUID(as_uuid=True), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    new_data = Column(JSON, nullable=True)
