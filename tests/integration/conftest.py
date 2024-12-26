from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from alembic import command, config
from app.common.enums.enums import DataTypeEnum, EntityTypeEnum, NodeTypeEnum, PlacementEnum, StatusEnum
from app.components.metric_set_trees.dal import MetricSetTreeDAL
from app.components.metric_set_trees.models.metric_set_tree import MetricSetTreeModel
from app.components.metric_set_trees.service import MetricSetTreeService
from app.components.metric_sets.dal import MetricSetDAL
from app.components.metric_sets.models.metric_set import MetricSetModel
from app.components.metric_sets.service import MetricSetService
from app.components.properties.dal import PropertyDAL
from app.components.properties.models.property import PropertyModel
from app.components.properties.service import PropertyService
from app.components.utils.meta_data_service import MetaDataService
from matter_persistence.redis.manager import CacheManager
from matter_persistence.redis.utils import get_connection_pool
from matter_persistence.sql.manager import DatabaseManager
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection
from testcontainers.core.container import DockerContainer
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer

_TEST_DB_USER = "metric-metadata-api"
_TEST_DB_PASSWORD = "Password!"
_TEST_DB_NAME = "metric-metadata"
_TEST_AWS_PORT = 4567


# Test Postgres Database for the integration tests
@pytest.fixture(scope="session")
def postgres_container() -> Generator[PostgresContainer, None, None]:
    with PostgresContainer(
        username=_TEST_DB_USER,
        password=_TEST_DB_PASSWORD,
        dbname=_TEST_DB_NAME,
    ) as postgres:
        yield postgres


# Test Redis Database for the integration tests
@pytest.fixture(scope="session")
def redis_container() -> Generator[RedisContainer, None, None]:
    with RedisContainer(
        username=_TEST_DB_USER,
        password=_TEST_DB_PASSWORD,
        dbname=_TEST_DB_NAME,
    ) as postgres:
        yield postgres


@pytest.fixture(scope="session", autouse=True)
def aws_localstack_container() -> Generator[DockerContainer, None, None]:
    with DockerContainer(
        image="localstack/localstack:latest-amd64",
    ).with_bind_ports(_TEST_AWS_PORT, _TEST_AWS_PORT) as aws_container:
        yield aws_container


@pytest.fixture
def database_manager(postgres_container: PostgresContainer) -> DatabaseManager:
    return DatabaseManager(
        postgres_container.get_connection_url(driver="asyncpg"),
        {"echo": True},
    )


@pytest.fixture
def cache_manager(redis_container: RedisContainer) -> CacheManager:
    return CacheManager(
        connection_pool=get_connection_pool(host=redis_container.get_container_host_ip(), port=redis_container.port)
    )


@pytest_asyncio.fixture
async def initialize_db(database_manager: DatabaseManager) -> AsyncGenerator[None, None]:
    def run_upgrade(connection, cfg):
        cfg.attributes["connection"] = connection
        command.upgrade(cfg, "head")

    alembic_config = config.Config("src/alembic.ini")
    alembic_config.set_main_option("script_location", "src/alembic")
    async with database_manager.connect() as conn:
        await conn.run_sync(run_upgrade, alembic_config)

    yield

    async with database_manager.connect() as conn:
        conn: AsyncConnection
        await conn.execute(text("DROP SCHEMA public CASCADE"))
        await conn.execute(text("CREATE SCHEMA public"))


@pytest.fixture
def property_dal(database_manager: DatabaseManager, initialize_db: None):
    return PropertyDAL(database_manager=database_manager)


@pytest.fixture
def property_service(property_dal):
    return PropertyService(dal=property_dal)


@pytest.fixture
def property_example():
    return PropertyModel(
        property_name="test_property",
        property_description="Some Description",
        entity_type=EntityTypeEnum.METRIC,
        data_type=DataTypeEnum.STRING,
    )


@pytest.fixture
def meta_data_service(property_service, cache_manager):
    return MetaDataService(property_service=property_service, cache_manager=cache_manager)


@pytest.fixture
def metric_set_tree_dal(database_manager: DatabaseManager, initialize_db: None):
    return MetricSetTreeDAL(database_manager=database_manager)


@pytest.fixture
def metric_set_tree_service(metric_set_tree_dal, meta_data_service):
    return MetricSetTreeService(dal=metric_set_tree_dal, meta_data_service=meta_data_service)


@pytest.fixture
def metric_set_tree_example():
    return MetricSetTreeModel(
        node_type=NodeTypeEnum.METRIC,
        node_depth=0,
        node_name="test_root",
        node_description="Test Description",
        meta_data={},
    )


@pytest.fixture
def metric_set_dal(database_manager: DatabaseManager, initialize_db: None):
    return MetricSetDAL(database_manager=database_manager)


@pytest.fixture
def metric_set_service(metric_set_dal, meta_data_service):
    return MetricSetService(dal=metric_set_dal, meta_data_service=meta_data_service)


@pytest.fixture
def metric_set_test_entry(metric_set_dal):
    return metric_set_dal.create_metric_set(
        MetricSetModel(
            status=StatusEnum.DEPLOYED,
            short_name="test_metric_set_entry",
            placement=PlacementEnum.REGULATORY,
            meta_data={},
        )
    )


@pytest.fixture
def metric_set_example():
    return MetricSetModel(
        status=StatusEnum.DEPLOYED, short_name="test_metric_set", placement=PlacementEnum.REGULATORY, meta_data={}
    )
