from matter_persistence.sql.base import CustomBase
from sqlalchemy import Column, Enum, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.common.enums.enums import PlacementEnum, StatusEnum


class MetricSetModel(CustomBase):
    __tablename__ = "metric_sets"

    status = Column(Enum(StatusEnum), nullable=False)
    short_name = Column(String(100), nullable=False)
    placement = Column(Enum(PlacementEnum), nullable=False)
    meta_data = Column(JSONB, nullable=True)

    metrics = relationship("MetricModel", back_populates="metric_set")
    metric_set_trees = relationship("MetricSetTreeModel", back_populates="metric_set")
