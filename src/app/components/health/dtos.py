from matter_persistence.foundation_model import FoundationModel
from pydantic import BaseModel, Field


class HealthStatusOutDTO(BaseModel):
    health: bool = Field(
        ...,
        description="Health Check Response",
    )


class HealthDeepStatusOutDTO(FoundationModel, HealthStatusOutDTO):
    database: bool = Field(
        ...,
        description="Health Check Database Response",
    )
    cache: bool = Field(
        ...,
        description="Health Check Cache Response",
    )
