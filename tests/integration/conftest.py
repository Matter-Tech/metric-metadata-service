import datetime
from typing import AsyncGenerator, Generator
from uuid import UUID, uuid4

import pytest
import pytest_asyncio
from alembic import command, config
from app.components.organizations.dal import OrganizationDAL
from app.components.organizations.models.organization import OrganizationModel
from app.components.organizations.service import OrganizationService
from matter_persistence.sql.manager import DatabaseManager
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection
from testcontainers.core.container import DockerContainer
from testcontainers.postgres import PostgresContainer

_TEST_DB_USER = "template-api"
_TEST_DB_PASSWORD = "Password!"
_TEST_DB_NAME = "template-api"

_TEST_ORGANISATION_CONFIG = {
    ("admin@website.com", "Apple", "Template", "Admin"),
    ("manager@website.com", "Amazon", "Template", "Manager"),
    ("api@website.com", "Tesla", "Template", "API"),
    ("app@website.com", "SpaceX", "Template", "App"),
    ("user@website.com", "Microsoft", "Template", "User"),
}


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

    alembic_config = config.Config("src/alembic.ini")
    alembic_config.set_main_option("script_location", "src/alembic")
    async with database_manager.connect() as conn:
        await conn.run_sync(run_upgrade, alembic_config)
    utc_now = "2024-01-01T00:00:00Z"
    async with database_manager.connect() as conn:
        for organisation in _TEST_ORGANISATION_CONFIG:
            await conn.execute(
                text(
                    f"INSERT INTO organizations"
                    f"(id, organization_email, organization_name, first_name, last_name, created, updated) "
                    f"VALUES "
                    f"{uuid4(), organisation[0], organisation[1], organisation[2], organisation[3], utc_now, utc_now}"
                )
            )

    yield

    async with database_manager.connect() as conn:
        conn: AsyncConnection
        await conn.execute(text("DROP SCHEMA public CASCADE"))
        await conn.execute(text("CREATE SCHEMA public"))


@pytest.fixture
def organization_dal(database_manager: DatabaseManager, initialize_db: None):
    # Create an instance of the UserDAL with required dependencies
    return OrganizationDAL(database_manager=database_manager)


@pytest.fixture
def organization_service(organization_dal):
    # Create an instance of the UserService with required dependencies
    return OrganizationService(dal=organization_dal)


@pytest.fixture
def organization_id() -> UUID:
    return uuid4()


@pytest.fixture
def organization(organization_id) -> OrganizationModel:
    organization_model = OrganizationModel(
        id=organization_id,
        organization_name="Dunder Mifflin Paper Company, Inc.",
        organization_email="testuser@example.com",
        first_name="FirstName",
        last_name="LastName",
    )
    organization_model.created = datetime.datetime.now(tz=datetime.timezone.utc)

    return organization_model
