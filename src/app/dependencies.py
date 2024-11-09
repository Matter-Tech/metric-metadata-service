from matter_persistence.redis.manager import CacheManager
from matter_persistence.redis.utils import get_connection_pool
from matter_persistence.sql.manager import DatabaseManager

from app.components.health.dal import HealthDAL
from app.components.health.service import HealthService
from app.components.metric_sets.dal import MetricSetDAL
from app.components.metric_sets.service import MetricSetService
from app.components.properties.dal import PropertyDAL
from app.components.properties.service import PropertyService
from app.env import SETTINGS

from app.components.metric_sets.models.metric_set import MetricSetModel
from app.components.metrics.models.metric import MetricModel
from app.components.metric_set_trees.models.metric_set_tree import MetricSetTreeModel
from app.components.data_metrics.models.data_metric import DataMetricModel


class Dependencies:
    _health_dal: HealthDAL
    _health_service: HealthService

    _property_service: PropertyService
    _property_dal: PropertyDAL

    _metric_set_service: MetricSetService
    _metric_set_dal: MetricSetDAL

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

        cls._property_dal = PropertyDAL(database_manager=cls.db_manager())
        cls._property_service = PropertyService(dal=cls._property_dal)

        cls._metric_set_dal = MetricSetDAL(database_manager=cls.db_manager())
        cls._metric_set_service = MetricSetService(dal=cls._metric_set_dal)

    @classmethod
    async def stop(cls):
        await cls._cache_manager.close_connection_pool()
        await cls._database_manager.close()

    @classmethod
    def health_service(cls) -> HealthService:
        return cls._health_service


    @classmethod
    def property_service(cls) -> PropertyService:
        return cls._property_service

    @classmethod
    def metric_set_service(cls) -> MetricSetService:
        return cls._metric_set_service

    @classmethod
    def cache_manager(cls) -> CacheManager:
        return cls._cache_manager

    @classmethod
    def db_manager(cls) -> DatabaseManager:
        return cls._database_manager
