from unittest.mock import MagicMock, AsyncMock

import pytest

from collector_db.AsyncDatabaseClient import AsyncDatabaseClient
from collector_db.DatabaseClient import DatabaseClient
from core.CoreLogger import CoreLogger
from source_collectors.auto_googler.AutoGooglerCollector import AutoGooglerCollector
from source_collectors.auto_googler.DTOs import AutoGooglerInputDTO

@pytest.mark.asyncio
async def test_autogoogler_collector():
    collector = AutoGooglerCollector(
        batch_id=1,
        dto=AutoGooglerInputDTO(
            urls_per_result=5,
            queries=["police"],
        ),
        logger = MagicMock(spec=CoreLogger),
        adb_client=AsyncMock(spec=AsyncDatabaseClient),
        raise_error=True
    )
    await collector.run()
    print(collector.data)