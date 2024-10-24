from uuid import UUID

from matter_persistence.foundation_model import FoundationModel
from pydantic import Field


class HelloWorldItemRequestModel(FoundationModel):
    id: UUID = Field(
        ...,
        description="Hello World Item Request",
    )
    value: str | None = None


class HelloWorldItemResponseModel(FoundationModel):
    id: UUID = Field(
        ...,
        description="Hello World Item Response",
    )
    value: str | None = None
