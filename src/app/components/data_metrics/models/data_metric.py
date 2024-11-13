from matter_persistence.sql.base import CustomBase
from sqlalchemy import UUID, Column, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship


class DataMetricModel(CustomBase):
    __tablename__ = "data_metrics"

    data_id = Column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
        comment="Field used to store the UUID to the data nodes which are updated every quarter.",
    )
    metric_type = Column(String(50), nullable=False, index=True)
    name = Column(String(100), nullable=False, index=True)
    meta_data = Column(JSONB, nullable=True)

    metrics = relationship("MetricModel", back_populates="data_metric")
