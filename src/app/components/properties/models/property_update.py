from pydantic import BaseModel

from app.components.properties.models.property import EntityTypeEnum, DataTypeEnum


class PropertyUpdateModel(BaseModel):
    property_name: str = None
    property_description: str = None

    data_type: DataTypeEnum = None
    entity_type: EntityTypeEnum = None

    is_required: bool = None
