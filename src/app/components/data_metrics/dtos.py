import uuid
from datetime import datetime, timezone
from typing import List

from matter_persistence.foundation_model import FoundationModel
from pydantic import BaseModel, Field


class DataMetricInDTO(BaseModel):
    data_id: uuid.UUID = Field(..., alias='dataId')
    metric_type: str = Field(..., max_length=50, alias='metricType')
    name: str = Field(..., max_length=100, alias='name')
    meta_data: dict | None = Field(None, alias='metaData')

class DataMetricUpdateInDTO(DataMetricInDTO):
    data_id: uuid.UUID | None = Field(None, alias='dataId')
    metric_type: str | None = Field(None, max_length=50, alias='metricType')
    name: str | None = Field(None, max_length=100, alias='name')
    meta_data: dict | None = Field(None, alias='metaData')

class DataMetricOutDTO(FoundationModel):
    id: uuid.UUID


class FullDataMetricOutDTO(DataMetricOutDTO):
    data_id: uuid.UUID = Field(None, alias='dataId')
    metric_type: str = Field(None, max_length=50, alias='metricType')
    name: str = Field(None, max_length=100, alias='name')
    meta_data: dict | None = Field(None, alias='metaData')

class DataMetricDeletionOutDTO(DataMetricOutDTO):
    deleted_at: datetime = Field(datetime.now(tz=timezone.utc), alias="deletedAt")


class DataMetricListOutDTO(FoundationModel):
    count: int
    data_metrics: List[FullDataMetricOutDTO]
