from pydantic import BaseModel

from app.components.properties.models.property import DataTypeEnum, EntityTypeEnum


class PropertyUpdateModel(BaseModel):
    property_name: str | None = None
    property_description: str | None = None

    data_type: DataTypeEnum | None = None
    entity_type: EntityTypeEnum | None = None

    is_required: bool | None = None
