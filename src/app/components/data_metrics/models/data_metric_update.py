import uuid

from pydantic import BaseModel


class DataMetricUpdateModel(BaseModel):
    data_id: uuid.UUID = None
    metric_type: str = None
    name: str = None
    meta_data: dict = None
