import uuid
from datetime import datetime, timezone
from typing import List

from matter_persistence.foundation_model import FoundationModel
from pydantic import BaseModel, Field

from app.common.enums.enums import PlacementEnum, StatusEnum


class MetricSetInDTO(BaseModel):
    status: StatusEnum = Field(..., alias="status")
    short_name: str = Field(..., max_length=100, alias="shortName")
    placement: PlacementEnum = Field(..., alias="placement")
    meta_data: dict = Field(..., alias="metaData")


class MetricSetUpdateInDTO(MetricSetInDTO):
    status: StatusEnum | None = Field(None, alias="status")
    short_name: str | None = Field(None, max_length=100, alias="shortName")
    placement: PlacementEnum | None = Field(None, alias="placement")
    meta_data: dict | None = Field(None, alias="metaData")


class MetricSetOutDTO(FoundationModel):
    id: uuid.UUID


class FullMetricSetOutDTO(MetricSetOutDTO):
    status: StatusEnum = Field(..., alias="status")
    short_name: str = Field(..., max_length=100, alias="shortName")
    placement: PlacementEnum = Field(..., alias="placement")
    meta_data: dict = Field(..., alias="metaData")


class MetricSetDeletionOutDTO(MetricSetOutDTO):
    deleted_at: datetime = Field(datetime.now(tz=timezone.utc), alias="deletedAt")


class MetricSetListOutDTO(FoundationModel):
    count: int
    metric_sets: List[FullMetricSetOutDTO]
