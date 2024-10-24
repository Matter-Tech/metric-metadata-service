from matter_persistence.redis.manager import CacheManager
from matter_persistence.sql.manager import DatabaseManager
from matter_persistence.sql.utils import is_database_alive


class HealthDAL:
    """
    This class represents a data access layer for health-related operations.

    Constructor:
        def __init__(
            self,
            cache_client: APICacheClient,
            database_manager: DatabaseSessionManager,
        )

    Methods:
        async def is_database_alive(self) -> bool
            - Checks if the database is alive by calling the is_database_alive function with the provided database session.

        async def is_cache_alive(self) -> bool
            - Checks if the cache is alive by calling the is_cache_alive function of the cache client.

    """

    def __init__(
        self,
        cache_manager: CacheManager,
        database_manager: DatabaseManager,
    ):
        self._cache_manager = cache_manager
        self._database_manager = database_manager

    async def is_database_alive(
        self,
    ) -> bool:
        return await is_database_alive(self._database_manager)

    async def is_cache_alive(
        self,
    ) -> bool:
        return await self._cache_manager.is_cache_alive()
