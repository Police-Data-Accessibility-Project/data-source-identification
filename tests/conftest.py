import pytest
from alembic.config import Config
from sqlalchemy import create_engine, inspect, MetaData
from sqlalchemy.orm import scoped_session, sessionmaker

from db.AsyncDatabaseClient import AsyncDatabaseClient
from db.DatabaseClient import DatabaseClient
from db.helper_functions import get_postgres_connection_string
from db.models import Base
from core.EnvVarManager import EnvVarManager
from tests.helpers.AlembicRunner import AlembicRunner
from tests.helpers.DBDataCreator import DBDataCreator
from util.helper_functions import load_from_environment


@pytest.fixture(autouse=True, scope="session")
def setup_and_teardown():
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
def wipe_database():
    """
    Wipe all data from database
    Returns:

    """
    conn = get_postgres_connection_string()
    engine = create_engine(conn)
    with engine.connect() as connection:
        for table in reversed(Base.metadata.sorted_tables):
            connection.execute(table.delete())
        connection.commit()


@pytest.fixture
def db_client_test(wipe_database) -> DatabaseClient:
    # Drop pre-existing table
    conn = get_postgres_connection_string()
    db_client = DatabaseClient(db_url=conn)
    yield db_client
    db_client.engine.dispose()

@pytest.fixture
def adb_client_test(wipe_database) -> AsyncDatabaseClient:
    conn = get_postgres_connection_string(is_async=True)
    adb_client = AsyncDatabaseClient(db_url=conn)
    yield adb_client
    adb_client.engine.dispose()

@pytest.fixture
def db_data_creator(db_client_test):
    db_data_creator = DBDataCreator(db_client=db_client_test)
    yield db_data_creator
