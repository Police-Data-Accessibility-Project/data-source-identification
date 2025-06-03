import asyncio
from unittest.mock import AsyncMock

import pytest

from src.api.endpoints.batch.dtos.get.logs import GetBatchLogsResponse
from src.api.endpoints.batch.dtos.get.summaries.response import GetBatchSummariesResponse
from src.api.endpoints.batch.dtos.get.summaries.summary import BatchSummary
from src.db.client.async_ import AsyncDatabaseClient
from src.db.dtos.batch_info import BatchInfo
from src.collectors.source_collectors.example.dtos.input import ExampleInputDTO
from src.collectors.source_collectors.example.core import ExampleCollector
from src.collectors.enums import CollectorType
from src.core.logger import AsyncCoreLogger
from src.core.enums import BatchStatus
from tests.helpers.patch_functions import block_sleep
from tests.automated.integration.api.conftest import disable_task_trigger


@pytest.mark.asyncio
async def test_example_collector(api_test_helper, monkeypatch):
    ath = api_test_helper

    barrier = await block_sleep(monkeypatch)

    # Temporarily disable task trigger
    disable_task_trigger(ath)


    logger = AsyncCoreLogger(adb_client=AsyncDatabaseClient(), flush_interval=1)
    await logger.__aenter__()
    ath.async_core.collector_manager.logger = logger

    dto = ExampleInputDTO(
        sleep_time=1
    )

    # Request Example Collector
    data = ath.request_validator.example_collector(
        dto=dto
    )
    batch_id = data["batch_id"]
    assert batch_id is not None
    assert data["message"] == "Started example collector."

    # Yield control so coroutine runs up to the barrier
    await asyncio.sleep(0)


    # Check that batch currently shows as In Process
    bsr: GetBatchSummariesResponse = ath.request_validator.get_batch_statuses(
        status=BatchStatus.IN_PROCESS
    )
    assert len(bsr.results) == 1
    bsi: BatchInfo = bsr.results[0]

    assert bsi.id == batch_id
    assert bsi.strategy == CollectorType.EXAMPLE.value
    assert bsi.status == BatchStatus.IN_PROCESS

    # Release the barrier to resume execution
    barrier.release()

    await ath.wait_for_all_batches_to_complete()

    csr: GetBatchSummariesResponse = ath.request_validator.get_batch_statuses(
        collector_type=CollectorType.EXAMPLE,
        status=BatchStatus.READY_TO_LABEL
    )

    assert len(csr.results) == 1
    bsi: BatchSummary = csr.results[0]

    assert bsi.id == batch_id
    assert bsi.strategy == CollectorType.EXAMPLE.value
    assert bsi.status == BatchStatus.READY_TO_LABEL

    bi: BatchSummary = ath.request_validator.get_batch_info(batch_id=batch_id)
    assert bi.status == BatchStatus.READY_TO_LABEL
    assert bi.url_counts.total == 2
    assert bi.parameters == dto.model_dump()
    assert bi.strategy == CollectorType.EXAMPLE.value
    assert bi.user_id is not None

    # Flush early to ensure logs are written
    await logger.flush_all()

    lr: GetBatchLogsResponse = ath.request_validator.get_batch_logs(batch_id=batch_id)

    assert len(lr.logs) > 0

    # Check that task was triggered
    ath.async_core.collector_manager.\
        post_collection_function_trigger.\
        trigger_or_rerun.assert_called_once()

    await logger.__aexit__(None, None, None)

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




