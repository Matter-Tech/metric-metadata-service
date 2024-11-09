import uuid

from pydantic import BaseModel

from app.common.enums.enums import NodeTypeEnum


class MetricSetTreeUpdateModel(BaseModel):
    metric_set_id: uuid.UUID = None

    node_type: NodeTypeEnum = None
    node_depth: int = None
    node_name: str = None
    node_description: str = None
    node_reference_id: str = None
    node_special: str = None
    meta_data: dict = None


