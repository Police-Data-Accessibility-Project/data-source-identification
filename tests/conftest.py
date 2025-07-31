import logging
from typing import Any, Generator, AsyncGenerator

import pytest
import pytest_asyncio
from aiohttp import ClientSession
from alembic.config import Config
from sqlalchemy import create_engine, inspect, MetaData
from sqlalchemy.orm import scoped_session, sessionmaker

from src.core.env_var_manager import EnvVarManager
from src.db.client.async_ import AsyncDatabaseClient
from src.db.client.sync import DatabaseClient
from src.db.helpers.connect import get_postgres_connection_string
from src.util.helper_functions import load_from_environment
from tests.helpers.alembic_runner import AlembicRunner
from tests.helpers.data_creator.core import DBDataCreator
from tests.helpers.setup.populate import populate_database
from tests.helpers.setup.wipe import wipe_database


@pytest.fixture(autouse=True, scope="session")
def setup_and_teardown():
    logging.disable(logging.INFO)
    # Set up environment variables that must be defined
    # outside of tests
    required_env_vars: dict = load_from_environment(
            keys=[
                "POSTGRES_USER",
                "POSTGRES_PASSWORD",
                "POSTGRES_HOST",
                "POSTGRES_PORT",
                "POSTGRES_DB",
            ]
        )
    # Add test environment variables
    test_env_vars = [
        "GOOGLE_API_KEY",
        "GOOGLE_CSE_ID",
        "PDAP_EMAIL",
        "PDAP_PASSWORD",
        "PDAP_API_KEY",
        "PDAP_API_URL",
        "DISCORD_WEBHOOK_URL",
        "OPENAI_API_KEY",
        "HUGGINGFACE_INFERENCE_API_KEY",
        "HUGGINGFACE_HUB_TOKEN"
    ]
    all_env_vars = required_env_vars.copy()
    for env_var in test_env_vars:
        all_env_vars[env_var] = "TEST"

    EnvVarManager.override(all_env_vars)

    conn = get_postgres_connection_string()
    engine = create_engine(conn)
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.attributes["connection"] = engine.connect()
    alembic_cfg.set_main_option(
        "sqlalchemy.url",
        get_postgres_connection_string()
    )
    live_connection = engine.connect()
    runner = AlembicRunner(
        alembic_config=alembic_cfg,
        inspector=inspect(live_connection),
        metadata=MetaData(),
        connection=live_connection,
        session=scoped_session(sessionmaker(bind=live_connection)),
    )
    try:
        runner.upgrade("head")
    except Exception as e:
        print("Exception while upgrading: ", e)
        print("Resetting schema")
        runner.reset_schema()
        runner.stamp("base")
        runner.upgrade("head")


    yield
    try:
        runner.downgrade("base")
    except Exception as e:
        print("Exception while downgrading: ", e)
        print("Resetting schema")
        runner.reset_schema()
        runner.stamp("base")
    finally:
        live_connection.close()
        engine.dispose()

@pytest.fixture
def wiped_database():
    """Wipe all data from database."""
    wipe_database(get_postgres_connection_string())



@pytest.fixture
def db_client_test(wiped_database) -> Generator[DatabaseClient, Any, None]:
    # Drop pre-existing table
    conn = get_postgres_connection_string()
    db_client = DatabaseClient(db_url=conn)
    yield db_client
    db_client.engine.dispose()

@pytest_asyncio.fixture
async def populated_database(wiped_database) -> None:
    conn = get_postgres_connection_string(is_async=True)
    adb_client = AsyncDatabaseClient(db_url=conn)
    await populate_database(adb_client)

@pytest_asyncio.fixture
async def adb_client_test(wiped_database) -> AsyncGenerator[AsyncDatabaseClient, Any]:
    conn = get_postgres_connection_string(is_async=True)
    adb_client = AsyncDatabaseClient(db_url=conn)
    yield adb_client
    adb_client.engine.dispose()

@pytest.fixture
def db_data_creator(
    db_client_test,
):
    db_data_creator = DBDataCreator(db_client=db_client_test)
    yield db_data_creator

@pytest.fixture
async def test_client_session() -> AsyncGenerator[ClientSession, Any]:
    async with ClientSession() as session:
        yield session