from matter_persistence.redis.manager import CacheManager
from matter_persistence.redis.utils import get_connection_pool
from matter_persistence.sql.manager import DatabaseManager

from app.components.health.dal import HealthDAL
from app.components.health.service import HealthService
from app.components.items.dal import ItemDAL
from app.components.items.service import ItemService
from app.components.organizations.dal import OrganizationDAL
from app.components.organizations.service import OrganizationService
from app.env import SETTINGS


class Dependencies:
    """
    Class: Dependencies

    This class represents a collection of dependencies used in the application.
    It provides methods to start the dependencies and access the services.

    Attributes:
    - _health_dal (HealthDAL): An instance of the HealthDAL class.
    - _health_service (HealthService): An instance of the HealthService class.
    - _item_dal (ItemDAL): An instance of the ItemDAL class.
    - _item_service (ItemService): An instance of the ItemService class.
    - _organization_dal (OrganizationDAL): An instance of the OrganizationDAL class.
    - _organization_service (OrganizationService): An instance of the OrganizationService class.
    - _database_session_manager (DatabaseSessionManager): An instance of the DatabaseSessionManager class.

    Methods:
    - start(): Initializes the dependencies by creating the necessary instances of the classes and setting the attributes.
    - stop(): Stops the connections to DB & cache.
    - health_service() -> HealthService: Returns the HealthService instance.
    - item_service() -> ItemService: Returns the ItemService instance.
    - organization_service() -> OrganizationService: Returns the OrganizationService instance.
    - cache_client() -> APICacheClient: Returns an instance of the APICacheClient class.
    - db_session() -> DatabaseSessionManager: Returns the DatabaseSessionManager instance.
    """

    _health_dal: HealthDAL
    _health_service: HealthService

    _item_dal: ItemDAL
    _item_service: ItemService

    _organization_service: OrganizationService
    _organization_dal: OrganizationDAL

    _database_manager: DatabaseManager
    _cache_manager: CacheManager

    @classmethod
    def start(cls):
        cls._database_manager = DatabaseManager(host=SETTINGS.db_url, engine_kwargs={"echo": True})
        cls._cache_manager = CacheManager(
            connection_pool=get_connection_pool(host=SETTINGS.cache_endpoint_url, port=SETTINGS.cache_port)
        )

        cls._health_dal = HealthDAL(cache_manager=cls.cache_manager(), database_manager=cls.db_manager())
        cls._health_service = HealthService(dal=cls._health_dal)

        cls._item_dal = ItemDAL(cache_manager=cls.cache_manager())
        cls._item_service = ItemService(dal=cls._item_dal)

        cls._organization_dal = OrganizationDAL(database_manager=cls.db_manager())
        cls._organization_service = OrganizationService(dal=cls._organization_dal)

    @classmethod
    async def stop(cls):
        await cls._cache_manager.close_connection_pool()
        await cls._database_manager.close()

    @classmethod
    def health_service(cls) -> HealthService:
        return cls._health_service

    @classmethod
    def item_service(cls) -> ItemService:
        return cls._item_service

    @classmethod
    def organization_service(cls) -> OrganizationService:
        return cls._organization_service

    @classmethod
    def cache_manager(cls) -> CacheManager:
        return cls._cache_manager

    @classmethod
    def db_manager(cls) -> DatabaseManager:
        return cls._database_manager
