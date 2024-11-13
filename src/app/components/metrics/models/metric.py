from matter_persistence.sql.base import CustomBase
from sqlalchemy import UUID, Column, Enum, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.common.enums.enums import StatusEnum


class MetricModel(CustomBase):
    __tablename__ = "metrics"

    # Foreign Keys
    metric_set_id = Column(UUID(as_uuid=True), ForeignKey("metric_sets.id"), nullable=False, index=True)
    parent_section_id = Column(UUID(as_uuid=True), ForeignKey("metric_set_trees.id"), nullable=True, index=True)
    parent_metric_id = Column(UUID(as_uuid=True), ForeignKey("metrics.id"), nullable=True, index=True)
    data_metric_id = Column(UUID(as_uuid=True), ForeignKey("data_metrics.id"), nullable=True, index=True)

    status = Column(Enum(StatusEnum), nullable=False)
    name = Column(String(100), nullable=False)
    name_suffix = Column(String(50), nullable=True)
    meta_data = Column(JSONB, nullable=True)

    metric_set = relationship("MetricSetModel", back_populates="metrics")
    parent_section = relationship("MetricSetTreeModel", back_populates="metrics")
    parent_metric = relationship(
        "MetricModel", primaryjoin="MetricModel.id == MetricModel.parent_metric_id", remote_side="MetricModel.id"
    )
    data_metric = relationship("DataMetricModel", back_populates="metrics")

    __table_args__ = (Index("ix_metric_metric_set_id_status", "metric_set_id", "status"),)
