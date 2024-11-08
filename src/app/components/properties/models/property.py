import uuid

from matter_persistence.sql.base import CustomBase
from sqlalchemy import UUID, Boolean, Column, Enum, String, Text

from app.common.enums.enums import DataTypeEnum, EntityTypeEnum


class PropertyModel(CustomBase):
    __tablename__ = "properties"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    property_name = Column(String(100), unique=True, index=True, nullable=False)
    property_description = Column(Text, index=True, nullable=True)
    data_type = Column(Enum(DataTypeEnum), nullable=False)
    entity_type = Column(Enum(EntityTypeEnum), index=True, nullable=False)
    is_required = Column(Boolean, default=False, nullable=False)
