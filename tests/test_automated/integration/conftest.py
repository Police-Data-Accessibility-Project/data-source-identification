
import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine

from collector_db.helper_functions import get_postgres_connection_string
from collector_db.models import Base
from core.CoreLogger import CoreLogger
from tests.helpers.DBDataCreator import DBDataCreator
from collector_db.DatabaseClient import DatabaseClient
from core.SourceCollectorCore import SourceCollectorCore

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
    command.upgrade(alembic_cfg, "head")
    engine.dispose()
    yield

@pytest.fixture
def db_client_test() -> DatabaseClient:
    # Drop pre-existing table
    conn = get_postgres_connection_string()
    engine = create_engine(conn)
    with engine.connect() as connection:
        for table in reversed(Base.metadata.sorted_tables):
            connection.execute(table.delete())
        connection.commit()

    # # # Run alembic to set at base
    # alembic_cfg = Config("alembic.ini")
    # alembic_cfg.attributes["connection"] = engine.connect()
    # alembic_cfg.set_main_option(
    #     "sqlalchemy.url",
    #     get_postgres_connection_string()
    # )
    # # command.stamp(alembic_cfg, "base")
    #
    #
    # # Then upgrade to head
    # command.upgrade(alembic_cfg, "head")

    db_client = DatabaseClient(db_url=conn)
    yield db_client
    db_client.engine.dispose()

@pytest.fixture
def test_core(db_client_test):
    with CoreLogger(
        db_client=db_client_test
    ) as logger:
        core = SourceCollectorCore(
            db_client=db_client_test,
            core_logger=logger,
            dev_mode=True
        )
        yield core
        core.shutdown()

@pytest.fixture
def db_data_creator(db_client_test):
    db_data_creator = DBDataCreator(db_client=db_client_test)
    yield db_data_creator
