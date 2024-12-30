import os
import threading

import pytest

from collector_db.helper_functions import get_postgres_connection_string
from collector_db.models import Base
from core.CoreLogger import CoreLogger
from tests.helpers.DBDataCreator import DBDataCreator
from collector_db.DatabaseClient import DatabaseClient
from core.SourceCollectorCore import SourceCollectorCore


@pytest.fixture
def db_client_test() -> DatabaseClient:
    db_client = DatabaseClient(db_url=get_postgres_connection_string())
    yield db_client
    db_client.engine.dispose()
    Base.metadata.drop_all(db_client.engine)

@pytest.fixture
def test_core(db_client_test):
    with CoreLogger() as logger:
        core = SourceCollectorCore(
            db_client=db_client_test,
            core_logger=logger
        )
        yield core
        core.shutdown()

@pytest.fixture
def db_data_creator(db_client_test):
    db_data_creator = DBDataCreator(db_client=db_client_test)
    yield db_data_creator

lock = threading.Lock()

@pytest.fixture
def thread_lock():
    with lock:
        yield