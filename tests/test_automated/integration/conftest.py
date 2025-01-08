
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


@pytest.fixture
def db_client_test() -> DatabaseClient:
    conn = get_postgres_connection_string()
    alembic_cfg = Config("alembic.ini")
    engine = create_engine(conn)
    alembic_cfg.attributes["connection"] = engine.connect()

    command.upgrade(alembic_cfg, "head")

    Base.metadata.create_all(engine)

    db_client = DatabaseClient(db_url=conn)
    yield db_client
    db_client.engine.dispose()
    Base.metadata.drop_all(db_client.engine)
    command.stamp(alembic_cfg, "base")


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
