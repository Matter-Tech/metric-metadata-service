import uuid
from datetime import datetime, timezone
from typing import List

from matter_persistence.foundation_model import FoundationModel
from pydantic import BaseModel, Field

from app.common.enums.enums import StatusEnum


class MetricInDTO(BaseModel):
    metric_set_id: uuid.UUID = Field(..., alias="metricSetId")
    parent_section_id: uuid.UUID | None = Field(None, alias="parentSectionId")
    parent_metric_id: uuid.UUID | None = Field(None, alias="parentMetricId")
    data_metric_id: uuid.UUID | None = Field(None, alias="dataMetricId")

    status: StatusEnum = Field(..., alias="status")
    name: str = Field(..., max_length=100, alias="name")
    name_suffix: str | None = Field(None, max_length=50, alias="nameSuffix")
    meta_data: dict | None = Field(None, alias="metaData")


class MetricUpdateInDTO(MetricInDTO):
    metric_set_id: uuid.UUID | None = Field(None, alias="metricSetId")
    parent_section_id: uuid.UUID | None = Field(None, alias="parentSectionId")
    parent_metric_id: uuid.UUID | None = Field(None, alias="parentMetricId")
    data_metric_id: uuid.UUID | None = Field(None, alias="dataMetricId")

    status: StatusEnum | None = Field(None, alias="status")
    name: str | None = Field(None, max_length=100, alias="name")
    name_suffix: str | None = Field(None, max_length=50, alias="nameSuffix")
    meta_data: dict | None = Field(None, alias="metaData")


class MetricOutDTO(FoundationModel):
    id: uuid.UUID


class FullMetricOutDTO(MetricOutDTO):
    metric_set_id: uuid.UUID = Field(..., alias="metricSetId")
    parent_section_id: uuid.UUID | None = Field(..., alias="parentSectionId")
    parent_metric_id: uuid.UUID | None = Field(..., alias="parentMetricId")
    data_metric_id: uuid.UUID | None = Field(..., alias="dataMetricId")

    status: StatusEnum = Field(..., alias="status")
    name: str = Field(..., max_length=100, alias="name")
    name_suffix: str | None = Field(..., max_length=50, alias="nameSuffix")
    meta_data: dict | None = Field(..., alias="metaData")


class MetricDeletionOutDTO(MetricOutDTO):
    deleted_at: datetime = Field(datetime.now(tz=timezone.utc), alias="deletedAt")


class MetricListOutDTO(FoundationModel):
    count: int
    metrics: List[FullMetricOutDTO]
