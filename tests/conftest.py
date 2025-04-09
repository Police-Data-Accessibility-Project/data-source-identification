import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, MetaData
from sqlalchemy.orm import scoped_session, sessionmaker

from collector_db.DatabaseClient import DatabaseClient
from collector_db.helper_functions import get_postgres_connection_string
from collector_db.models import Base
from helpers.AlembicRunner import AlembicRunner
from tests.helpers.DBDataCreator import DBDataCreator


@pytest.fixture(autouse=True, scope="session")
def setup_and_teardown():
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
        runner.reset_schema()
        runner.stamp("base")
        runner.upgrade("head")

    live_connection.close()
    engine.dispose()
    yield

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
def db_data_creator(db_client_test):
    db_data_creator = DBDataCreator(db_client=db_client_test)
    yield db_data_creator
