from unittest.mock import MagicMock

import pytest

from src.collectors.manager import AsyncCollectorManager
from src.core.core import AsyncCore
from src.core.logger import AsyncCoreLogger
from src.db.client.async_ import AsyncDatabaseClient


@pytest.fixture
def test_async_core(adb_client_test):
    logger = AsyncCoreLogger(
        adb_client=adb_client_test
    )
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
    logger.shutdown()