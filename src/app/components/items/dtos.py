import uuid

from matter_persistence.foundation_model import FoundationModel
from pydantic import Field


class ExtendedHelloWorldItemInDTO(FoundationModel):
    id: uuid.UUID = Field(
        uuid.uuid4(),
        description="Hello World Request",
    )


class BaseHelloWorldItemOutDTO(FoundationModel):
    id: uuid.UUID


class ExtendedHelloWorldItemOutDTO(BaseHelloWorldItemOutDTO):
    value: str | None = None
