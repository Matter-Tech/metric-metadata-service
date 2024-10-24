from pydantic import BaseModel


class HealthStatusModel(BaseModel):
    database: bool
    cache: bool
    health: bool
