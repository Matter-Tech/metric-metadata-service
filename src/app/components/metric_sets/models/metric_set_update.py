from pydantic import BaseModel

from app.common.enums.enums import PlacementEnum, StatusEnum


class MetricSetUpdateModel(BaseModel):
    status: StatusEnum = None
    short_name: str = None
    placement: PlacementEnum = None
    meta_data: dict = None
