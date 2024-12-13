import uuid
from datetime import datetime, timezone
from typing import List

from matter_persistence.foundation_model import FoundationModel
from pydantic import BaseModel, Field, field_validator

from app.components.properties.models.property import DataTypeEnum, EntityTypeEnum


class PropertyInDTO(BaseModel):
    property_name: str = Field(..., max_length=100, alias="propertyName")
    property_description: str | None = Field(None, alias="propertyDescription")
    data_type: DataTypeEnum = Field(..., alias="dataType")
    entity_type: EntityTypeEnum = Field(..., alias="entityType")
    is_required: bool = Field(..., alias="isRequired")

    @field_validator("property_name")
    def validate_property_name(cls, value):
        if not value.isalpha():
            raise ValueError(
                "Property Name must only contain alphabetic characters (no spaces, numbers, or special characters)."
            )
        return value

    @field_validator("property_description")
    def validate_property_description(cls, value):
        if value and len(value.strip()) == 0:
            raise ValueError("Property Description cannot be only whitespace.")
        return value


class PropertyUpdateInDTO(PropertyInDTO):
    property_name: str | None = Field(None, max_length=100, alias="propertyName")
    property_description: str | None = Field(None, alias="propertyDescription")
    data_type: DataTypeEnum | None = Field(None, alias="dataType")
    entity_type: EntityTypeEnum | None = Field(None, alias="entityType")
    is_required: bool | None = Field(None, alias="isRequired")

    @field_validator("property_name")
    def validate_property_name(cls, value):
        if value and not value.isalpha():
            raise ValueError(
                "Property Name must only contain alphabetic characters (no spaces, numbers, or special characters)."
            )
        return value

    @field_validator("property_description")
    def validate_property_description(cls, value):
        if value and len(value.strip()) == 0:
            raise ValueError("Property Description cannot be only whitespace.")
        return value


class PropertyOutDTO(FoundationModel):
    id: uuid.UUID


class FullPropertyOutDTO(PropertyOutDTO):
    property_name: str = Field(..., max_length=100, alias="propertyName")
    property_description: str | None = Field(None, alias="propertyDescription")
    data_type: DataTypeEnum = Field(..., alias="dataType")
    entity_type: EntityTypeEnum = Field(..., alias="entityType")
    is_required: bool = Field(..., alias="isRequired")


class PropertyDeletionOutDTO(PropertyOutDTO):
    deleted_at: datetime = Field(datetime.now(tz=timezone.utc), alias="deletedAt")


class PropertyListOutDTO(FoundationModel):
    count: int
    properties: List[FullPropertyOutDTO]
