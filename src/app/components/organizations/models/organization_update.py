from pydantic import BaseModel


class OrganizationUpdateModel(BaseModel):
    organization_name: str = None
    organization_email: str = None
    first_name: str = None
    last_name: str = None
