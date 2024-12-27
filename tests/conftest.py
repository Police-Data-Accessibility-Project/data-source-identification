import os

import pytest

from tests.source_collector.helpers.constants import TEST_DATABASE_URL, TEST_DATABASE_FILENAME
from collector_db.DatabaseClient import DatabaseClient
from core.CoreInterface import CoreInterface
from core.SourceCollectorCore import SourceCollectorCore


@pytest.fixture
def db_client_test() -> DatabaseClient:
    db_client = DatabaseClient(TEST_DATABASE_URL)
    yield db_client
    db_client.engine.dispose()
    os.remove(TEST_DATABASE_FILENAME)

@pytest.fixture
def test_core_interface(db_client_test):
    core = SourceCollectorCore(
        db_client=db_client_test
    )
    ci = CoreInterface(core=core)
    yield ci