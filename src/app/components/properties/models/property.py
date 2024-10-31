import uuid

from matter_persistence.sql.base import CustomBase
from sqlalchemy import Column, String, Boolean, Text, Enum, UUID

import enum

class DataTypeEnum(enum.Enum):
    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    DATETIME = "datetime"

class EntityTypeEnum(enum.Enum):
    METRIC = "metric"
    METRIC_SET = "metric_set"
    METRIC_HIERARCHY = "metric_hierarchy"
    METRIC_DATA = "metric_data"

class PropertyModel(CustomBase):
    __tablename__ = "properties"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)

    property_name = Column(String(100), unique=True, index=True, nullable=False)
    property_description = Column(Text, unique=True, index=True)

    data_type = Column(Enum(DataTypeEnum), nullable=False)
    entity_type = Column(Enum(EntityTypeEnum), index=True, nullable=False)

    is_required = Column(Boolean, default=False, nullable=False)
