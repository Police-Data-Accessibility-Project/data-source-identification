from unittest.mock import MagicMock

import pytest

from collector_db.AsyncDatabaseClient import AsyncDatabaseClient
from collector_manager.AsyncCollectorManager import AsyncCollectorManager
from core.AsyncCore import AsyncCore
from core.CoreLogger import CoreLogger
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


@pytest.fixture
def test_async_core(db_client_test):
    with CoreLogger(
        db_client=db_client_test
    ) as logger:
        adb_client = AsyncDatabaseClient()
        core = AsyncCore(
            adb_client=adb_client,
            task_manager=MagicMock(),
            collector_manager=AsyncCollectorManager(
                adb_client=adb_client,
                logger=logger,
                dev_mode=True
            ),
        )
        yield core
        core.shutdown()