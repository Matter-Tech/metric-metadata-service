from matter_observability.metrics import (
    count_occurrence,
    measure_processing_time,
)

from .dal import HealthDAL
from .models import HealthStatusModel


class HealthService:
    """

    The `HealthService` class represents a service that provides health status information about the system. It interacts with a `HealthDAL` object to retrieve health status data from different sources.

    Attributes:
        _dal (HealthDAL): The data access layer object used to retrieve health status information from the system.

    Methods:
        get_health_status: Retrieves the health status of the system.

    """

    def __init__(
        self,
        dal: HealthDAL,
    ):
        self._dal = dal

    @count_occurrence(label="health")
    @measure_processing_time(label="health")
    async def get_health_status(
        self,
    ) -> HealthStatusModel:
        database_alive = await self._dal.is_database_alive()
        cache_alive = await self._dal.is_cache_alive()

        return HealthStatusModel(
            database=database_alive,
            cache=cache_alive,
            health=database_alive and cache_alive,
        )
