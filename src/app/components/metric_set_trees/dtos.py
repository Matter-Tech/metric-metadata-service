import uuid
from datetime import datetime, timezone
from typing import List

from matter_persistence.foundation_model import FoundationModel
from pydantic import BaseModel, Field

from app.common.enums.enums import NodeTypeEnum


class MetricSetTreeInDTO(BaseModel):
    metric_set_id: uuid.UUID = Field(..., alias="metricSetId")
    node_type: NodeTypeEnum = Field(..., alias="nodeType")
    node_depth: int = Field(..., alias="nodeDepth")
    node_name: str = Field(..., max_length=100, alias="nodeName")
    node_description: str | None = Field(None, alias="nodeDescription")
    node_reference_id: str | None = Field(None, alias="nodeReferenceId")
    node_special: str | None = Field(None, alias="nodeSpecial")
    meta_data: dict | None = Field(..., alias="metaData")


class MetricSetTreeUpdateInDTO(MetricSetTreeInDTO):
    metric_set_id: uuid.UUID | None = Field(None, alias="metricSetId")
    node_type: NodeTypeEnum | None = Field(None, alias="nodeType")
    node_depth: int | None = Field(None, alias="nodeDepth")
    node_name: str | None = Field(None, max_length=100, alias="nodeName")
    node_description: str | None = Field(None, alias="nodeDescription")
    node_reference_id: str | None = Field(None, alias="nodeReferenceId")
    node_special: str | None = Field(None, alias="nodeSpecial")
    meta_data: dict | None = Field(None, alias="metaData")


class MetricSetTreeOutDTO(FoundationModel):
    id: uuid.UUID


class FullMetricSetTreeOutDTO(MetricSetTreeOutDTO):
    metric_set_id: uuid.UUID = Field(..., alias="metricSetId")
    node_type: NodeTypeEnum = Field(..., alias="nodeType")
    node_depth: int = Field(..., alias="nodeDepth")
    node_name: str | None = Field(None, max_length=100, alias="nodeName")
    node_description: str | None = Field(None, alias="nodeDescription")
    node_reference_id: str | None = Field(None, alias="nodeReferenceId")
    node_special: str | None = Field(None, alias="nodeSpecial")
    meta_data: dict | None = Field(None, alias="metaData")


class MetricSetTreeDeletionOutDTO(MetricSetTreeOutDTO):
    deleted_at: datetime = Field(datetime.now(tz=timezone.utc), alias="deletedAt")


class MetricSetTreeListOutDTO(FoundationModel):
    count: int
    metric_set_trees: List[FullMetricSetTreeOutDTO]
