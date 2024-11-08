from matter_persistence.sql.base import CustomBase
from sqlalchemy import JSON, Column, String


class DataMetricModel(CustomBase):
    __tablename__ = "data_metrics"

    metric_type = Column(String(50), nullable=False)
    name = Column(String(100), nullable=False)
    meta_data = Column(JSON, nullable=True)
