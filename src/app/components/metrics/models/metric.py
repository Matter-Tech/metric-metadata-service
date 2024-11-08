from matter_persistence.sql.base import CustomBase
from sqlalchemy import JSON, UUID, Column, Enum, ForeignKey, String

from app.common.enums.enums import StatusEnum


class MetricModel(CustomBase):
    __tablename__ = "metrics"

    metric_set_id = Column(UUID(as_uuid=True), ForeignKey("metric_sets.id"), nullable=False)
    parent_section_id = Column(UUID(as_uuid=True), ForeignKey("metric_set_trees.id"), nullable=True)
    parent_metric_id = Column(UUID(as_uuid=True), ForeignKey("metrics.id"), nullable=True)
    data_metric_id = Column(UUID(as_uuid=True), ForeignKey("metric_set_trees.id"), nullable=True)
    status = Column(Enum(StatusEnum), nullable=False)
    name = Column(String(100), nullable=False)
    name_suffix = Column(String(50), nullable=True)
    meta_data = Column(JSON, nullable=True)
