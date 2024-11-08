import uuid

from matter_persistence.sql.base import CustomBase
from sqlalchemy import JSON, UUID, Column, Enum, String

from app.common.enums.enums import PlacementEnum, StatusEnum


class MetricSetModel(CustomBase):
    __tablename__ = "metric_sets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ms_id = Column(String(100), unique=True, nullable=False)
    status = Column(Enum(StatusEnum), nullable=False)
    short_name = Column(String(100), nullable=False)
    placement = Column(Enum(PlacementEnum), nullable=False)
    meta_data = Column(JSON, nullable=True)
