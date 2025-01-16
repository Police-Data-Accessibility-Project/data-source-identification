
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

