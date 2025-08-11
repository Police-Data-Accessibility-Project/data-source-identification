from unittest.mock import AsyncMock

import pytest

from src.api.endpoints.batch.dtos.get.logs import GetBatchLogsResponse
from src.api.endpoints.batch.dtos.get.summaries.summary import BatchSummary
from src.collectors.impl.example.core import ExampleCollector
from src.collectors.impl.example.dtos.input import ExampleInputDTO
from src.core.enums import BatchStatus
from src.core.logger import AsyncCoreLogger
from src.db.client.async_ import AsyncDatabaseClient


@pytest.mark.asyncio
async def test_example_collector_error(api_test_helper, monkeypatch):
    """
    Test that when an error occurs in a collector, the batch is properly update
    """
    ath = api_test_helper

    logger = AsyncCoreLogger(adb_client=AsyncDatabaseClient(), flush_interval=1)
    await logger.__aenter__()
    ath.async_core.collector_manager.logger = logger

    # Patch the collector to raise an exception during run_implementation
    mock = AsyncMock()
    mock.side_effect = Exception("Collector failed!")
    monkeypatch.setattr(ExampleCollector, 'run_implementation', mock)

    dto = ExampleInputDTO(
            sleep_time=1
    )

    data = ath.request_validator.example_collector(
        dto=dto
    )
    batch_id = data["batch_id"]
    assert batch_id is not None
    assert data["message"] == "Started example collector."

    await ath.wait_for_all_batches_to_complete()

    bi: BatchSummary = ath.request_validator.get_batch_info(batch_id=batch_id)

    assert bi.status == BatchStatus.ERROR

    # Check there are logs
    assert not logger.log_queue.empty()
    await logger.flush_all()
    assert logger.log_queue.empty()

    gbl: GetBatchLogsResponse = ath.request_validator.get_batch_logs(batch_id=batch_id)
    assert gbl.logs[-1].log == "Error: Collector failed!"
    await logger.__aexit__(None, None, None)
