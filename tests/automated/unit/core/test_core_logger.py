import asyncio
from unittest.mock import AsyncMock

import pytest

from src.db.models.impl.log.pydantic.info import LogInfo
from src.core.logger import AsyncCoreLogger


@pytest.mark.asyncio
async def test_logger_flush():
    mock_adb_client = AsyncMock()
    async with AsyncCoreLogger(flush_interval=0.01, adb_client=mock_adb_client) as logger:

        # Add logs
        await logger.log(LogInfo(log="Log 1", batch_id=1))
        await logger.log(LogInfo(log="Log 2", batch_id=1))

        # Wait for the flush interval
        await asyncio.sleep(0.02)

        # Verify logs were flushed
        mock_adb_client.insert_logs.assert_called_once()
        flushed_logs = mock_adb_client.insert_logs.call_args[1]['log_infos']
        assert len(flushed_logs) == 2
        assert flushed_logs[0].log == "Log 1"


