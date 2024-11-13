import uuid

from pydantic import BaseModel

from app.common.enums.enums import StatusEnum


class MetricUpdateModel(BaseModel):
    metric_set_id: uuid.UUID = None
    parent_section_id: uuid.UUID = None
    parent_metric_id: uuid.UUID = None
    data_metric_id: uuid.UUID = None

    status: StatusEnum = None
    name: str = None
    name_suffix: str = None
    meta_data: dict = None
