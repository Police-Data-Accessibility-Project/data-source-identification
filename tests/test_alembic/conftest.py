import pytest
from alembic.config import Config
from sqlalchemy import create_engine, inspect, MetaData
from sqlalchemy.orm import scoped_session, sessionmaker

from collector_db.helper_functions import get_postgres_connection_string
from test_alembic.AlembicRunner import AlembicRunner


@pytest.fixture()
def alembic_config():
    alembic_cfg = Config("alembic.ini")
    yield alembic_cfg


@pytest.fixture()
def db_engine():
    engine = create_engine(get_postgres_connection_string())
    yield engine
    engine.dispose()


@pytest.fixture()
def connection(db_engine):
    connection = db_engine.connect()
    yield connection
    connection.close()


@pytest.fixture()
def alembic_runner(connection, alembic_config) -> AlembicRunner:
    alembic_config.attributes["connection"] = connection
    alembic_config.set_main_option(
        "sqlalchemy.url",
        get_postgres_connection_string()
    )
    runner = AlembicRunner(
        alembic_config=alembic_config,
        inspector=inspect(connection),
        metadata=MetaData(),
        connection=connection,
        session=scoped_session(sessionmaker(bind=connection)),
    )
    try:
        runner.downgrade("base")
    except Exception as e:
        runner.reset_schema()
        runner.stamp("base")
    print("Running test")
    yield runner
    print("Test complete")
    runner.session.close()
    try:
        runner.downgrade("base")
    except Exception as e:
        runner.reset_schema()
        runner.stamp("base")
