from matter_persistence.sql.base import CustomBase
from sqlalchemy import JSON, UUID, Column, Enum, ForeignKey, Integer, String, Text

from app.common.enums.enums import NodeTypeEnum


class MetricSetTreeModel(CustomBase):
    __tablename__ = "metric_set_trees"

    metric_set_id = Column(UUID(as_uuid=True), ForeignKey("metric_sets.id"), nullable=False)
    node_type = Column(Enum(NodeTypeEnum), nullable=False)
    node_depth = Column(Integer, nullable=False)
    node_name = Column(String(100), nullable=False)
    node_description = Column(Text, nullable=True)
    node_reference_id = Column(String(100), nullable=False)
    node_special = Column(String(100), nullable=True)
    meta_data = Column(JSON, nullable=True)
