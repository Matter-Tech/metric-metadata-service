from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from alembic import command, config
from app.common.enums.enums import DataTypeEnum, EntityTypeEnum
from app.components.properties.dal import PropertyDAL
from app.components.properties.models.property import PropertyModel
from app.components.properties.service import PropertyService
from matter_persistence.sql.manager import DatabaseManager
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection
from testcontainers.core.container import DockerContainer
from testcontainers.postgres import PostgresContainer

_TEST_DB_USER = "metric-metadata-api"
_TEST_DB_PASSWORD = "Password!"
_TEST_DB_NAME = "metric-metadata"


@pytest.fixture(scope="session")
def postgres_container() -> Generator[PostgresContainer, None, None]:
    with PostgresContainer(
        username=_TEST_DB_USER,
        password=_TEST_DB_PASSWORD,
        dbname=_TEST_DB_NAME,
    ) as postgres:
        yield postgres


@pytest.fixture(scope="session", autouse=True)
def aws_localstack_container() -> Generator[DockerContainer, None, None]:
    with DockerContainer(
        image="localstack/localstack:latest-amd64",
    ).with_bind_ports(4566, 4566) as aws_container:
        yield aws_container


@pytest.fixture
def database_manager(postgres_container: PostgresContainer) -> DatabaseManager:
    return DatabaseManager(
        postgres_container.get_connection_url(driver="asyncpg"),
        {"echo": True},
    )


@pytest_asyncio.fixture
async def initialize_db(database_manager: DatabaseManager) -> AsyncGenerator[None, None]:
    def run_upgrade(connection, cfg):
        cfg.attributes["connection"] = connection
        command.upgrade(cfg, "head")

    alembic_config = config.Config("../src/alembic.ini")
    alembic_config.set_main_option("script_location", "../src/alembic")
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
