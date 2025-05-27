from unittest.mock import AsyncMock

import pytest

from src.db import AsyncDatabaseClient
from src.core.AsyncCoreLogger import AsyncCoreLogger
from src.source_collectors.auto_googler.AutoGooglerCollector import AutoGooglerCollector
from src.source_collectors.auto_googler.DTOs import AutoGooglerInputDTO

@pytest.mark.asyncio
async def test_autogoogler_collector():
    collector = AutoGooglerCollector(
        batch_id=1,
        dto=AutoGooglerInputDTO(
            urls_per_result=5,
            queries=["police"],
        ),
        logger = AsyncMock(spec=AsyncCoreLogger),
        adb_client=AsyncMock(spec=AsyncDatabaseClient),
        raise_error=True
    )
    await collector.run()
    print(collector.data)