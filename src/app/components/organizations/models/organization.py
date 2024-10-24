from matter_persistence.sql.base import CustomBase
from sqlalchemy import Column, String


class OrganizationModel(CustomBase):
    __tablename__ = "organizations"

    organization_name = Column(String(100), unique=True, index=True, nullable=False)
    organization_email = Column(String(100), unique=True, index=True, nullable=False)

    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
