from matter_persistence.redis.manager import CacheManager
from matter_persistence.redis.utils import get_connection_pool
from matter_persistence.sql.manager import DatabaseManager

from app.components.data_metrics.dal import DataMetricDAL
from app.components.data_metrics.service import DataMetricService
from app.components.events.dal import EventDAL
from app.components.events.service import EventService
from app.components.health.dal import HealthDAL
from app.components.health.service import HealthService
from app.components.metric_set_trees.dal import MetricSetTreeDAL
from app.components.metric_set_trees.service import MetricSetTreeService
from app.components.metric_sets.dal import MetricSetDAL
from app.components.metric_sets.service import MetricSetService
from app.components.metrics.dal import MetricDAL
from app.components.metrics.service import MetricService
from app.components.properties.dal import PropertyDAL
from app.components.properties.service import PropertyService
from app.components.utils.meta_data_service import MetaDataService
from app.env import SETTINGS


class Dependencies:
    _health_dal: HealthDAL
    _health_service: HealthService

    _property_service: PropertyService
    _property_dal: PropertyDAL

    _metric_set_service: MetricSetService
    _metric_set_dal: MetricSetDAL

    _metric_set_tree_service: MetricSetTreeService
    _metric_set_tree_dal: MetricSetTreeDAL

    _data_metric_service: DataMetricService
    _data_metric_dal: DataMetricDAL

    _metric_service: MetricService
    _metric_dal: MetricDAL

    _event_service: EventService
    _event_dal: EventDAL

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

        cls._event_dal = EventDAL(database_manager=cls.db_manager())
        cls._event_service = EventService(dal=cls._event_dal)

        cls._property_dal = PropertyDAL(database_manager=cls.db_manager())
        cls._property_service = PropertyService(dal=cls._property_dal)

        cls._meta_data_service = MetaDataService(property_service=cls._property_service)

        cls._metric_set_dal = MetricSetDAL(database_manager=cls.db_manager())
        cls._metric_set_service = MetricSetService(dal=cls._metric_set_dal, meta_data_service=cls._meta_data_service)

        cls._metric_set_tree_dal = MetricSetTreeDAL(database_manager=cls.db_manager())
        cls._metric_set_tree_service = MetricSetTreeService(
            dal=cls._metric_set_tree_dal, meta_data_service=cls._meta_data_service
        )

        cls._data_metric_dal = DataMetricDAL(database_manager=cls.db_manager())
        cls._data_metric_service = DataMetricService(dal=cls._data_metric_dal, meta_data_service=cls._meta_data_service)

        cls._metric_dal = MetricDAL(database_manager=cls.db_manager())
        cls._metric_service = MetricService(dal=cls._metric_dal, meta_data_service=cls._meta_data_service)

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
    def metric_set_tree_service(cls) -> MetricSetTreeService:
        return cls._metric_set_tree_service

    @classmethod
    def data_metric_service(cls) -> DataMetricService:
        return cls._data_metric_service

    @classmethod
    def metric_service(cls) -> MetricService:
        return cls._metric_service

    @classmethod
    def event_service(cls) -> EventService:
        return cls._event_service

    @classmethod
    def cache_manager(cls) -> CacheManager:
        return cls._cache_manager

    @classmethod
    def db_manager(cls) -> DatabaseManager:
        return cls._database_manager
