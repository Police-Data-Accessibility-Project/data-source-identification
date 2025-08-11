from typing import Any, Generator

import pytest
from alembic.config import Config
from sqlalchemy import create_engine, inspect, MetaData, Engine, Connection
from sqlalchemy.orm import scoped_session, sessionmaker

from src.db.helpers.connect import get_postgres_connection_string
from tests.helpers.alembic_runner import AlembicRunner


@pytest.fixture()
def alembic_config() -> Generator[Config, Any, None]:
    alembic_cfg = Config("alembic.ini")
    yield alembic_cfg


@pytest.fixture()
def db_engine() -> Generator[Engine, Any, None]:
    engine = create_engine(get_postgres_connection_string())
    yield engine
    engine.dispose()


@pytest.fixture()
def connection(db_engine) -> Generator[Connection, Any, None]:
    connection = db_engine.connect()
    yield connection
    connection.close()


@pytest.fixture()
def alembic_runner(connection, alembic_config) -> Generator[AlembicRunner, Any, None]:
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
