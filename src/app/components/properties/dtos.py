import uuid
from datetime import datetime, timezone
from typing import List

from matter_persistence.foundation_model import FoundationModel
from pydantic import BaseModel, Field, field_validator

from app.components.properties.models.property import DataTypeEnum, EntityTypeEnum


class PropertyInDTO(BaseModel):
    property_name: str = Field(..., max_length=100, alias="propertyName")
    property_description: str = Field(..., alias="propertyDescription")
    data_type: DataTypeEnum = Field(..., alias="dataType")
    entity_type: EntityTypeEnum = Field(..., alias="entityType")
    is_required: bool = Field(..., alias="isRequired")

    @field_validator("property_name")
    def validate_property_name(cls, property_name):
        if any(char.isdigit() for char in property_name):
            raise ValueError("Property Name must contain only alphabetic characters")
        if len(property_name) == 0:
            raise ValueError("Property Name cannot be empty")
        return property_name


class PropertyUpdateInDTO(PropertyInDTO):
    property_name: str | None = Field(None, max_length=100, alias="propertyName")
    property_description: str | None = Field(None, alias="propertyDescription")
    data_type: DataTypeEnum | None = Field(None, alias="dataType")
    entity_type: EntityTypeEnum | None = Field(None, alias="entityType")
    is_required: bool | None = Field(None, alias="isRequired")


class PropertyOutDTO(FoundationModel):
    id: uuid.UUID


class FullPropertyOutDTO(PropertyOutDTO):
    property_name: str = Field(..., max_length=100, alias="propertyName")
    property_description: str = Field(..., alias="propertyDescription")
    data_type: DataTypeEnum = Field(..., alias="dataType")
    entity_type: EntityTypeEnum = Field(..., alias="entityType")
    is_required: bool = Field(..., alias="isRequired")


class PropertyDeletionOutDTO(PropertyOutDTO):
    deleted_at: datetime = Field(datetime.now(tz=timezone.utc), alias="deletedAt")


class PropertyListOutDTO(FoundationModel):
    count: int
    properties: List[FullPropertyOutDTO]
