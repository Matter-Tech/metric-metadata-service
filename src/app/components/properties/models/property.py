from matter_persistence.sql.base import CustomBase
from sqlalchemy import Boolean, Column, Enum, String, Text, UniqueConstraint

from app.common.enums.enums import DataTypeEnum, EntityTypeEnum


class PropertyModel(CustomBase):
    __tablename__ = "properties"

    property_name = Column(String(100), index=True, nullable=False)
    property_description = Column(Text, nullable=True)
    data_type = Column(Enum(DataTypeEnum), nullable=False)
    entity_type = Column(Enum(EntityTypeEnum), index=True, nullable=False)
    is_required = Column(Boolean, default=False, nullable=False)

    __table_args__ = (
        UniqueConstraint('property_name', 'entity_type', name='uq_property_name_entity_type'),
    )