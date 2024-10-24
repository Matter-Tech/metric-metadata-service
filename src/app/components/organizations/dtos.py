import uuid
from datetime import datetime, timezone
from typing import List

from matter_persistence.foundation_model import FoundationModel
from pydantic import BaseModel, EmailStr, Field, field_validator


class OrganizationInDTO(BaseModel):
    organization_name: str = Field(..., max_length=100, alias="organizationName")
    organization_email: EmailStr = Field(..., alias="organizationEmail")
    first_name: str = Field(..., max_length=100, alias="firstName")
    last_name: str = Field(..., max_length=100, alias="lastName")

    @field_validator("organization_name")
    def validate_organization_name(cls, organization_name, **kwargs):
        if any(char.isdigit() for char in organization_name):
            raise ValueError("Organization Name must contain only alphabetic characters")
        return organization_name


class OrganizationUpdateInDTO(BaseModel):
    organization_name: str = Field(..., max_length=100, alias="organizationName")
    first_name: str = Field(..., max_length=100, alias="firstName")
    last_name: str = Field(..., max_length=100, alias="lastName")


class OrganizationOutDTO(FoundationModel):
    id: uuid.UUID


class FullOrganizationOutDTO(OrganizationOutDTO):
    organization_name: str = Field(..., alias="organizationName")
    organization_email: EmailStr = Field(..., alias="organizationEmail")
    first_name: str = Field(..., alias="firstName")
    last_name: str = Field(..., alias="lastName")


class OrganizationDeletionOutDTO(OrganizationOutDTO):
    deleted_at: datetime = Field(datetime.now(tz=timezone.utc), alias="deletedAt")


class OrganizationListOutDTO(FoundationModel):
    count: int
    organizations: List[FullOrganizationOutDTO]
