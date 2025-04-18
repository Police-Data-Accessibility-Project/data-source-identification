import asyncio
from unittest.mock import AsyncMock

import pytest

from collector_db.AsyncDatabaseClient import AsyncDatabaseClient
from collector_db.DTOs.BatchInfo import BatchInfo
from collector_manager.DTOs.ExampleInputDTO import ExampleInputDTO
from collector_manager.ExampleCollector import ExampleCollector
from collector_manager.enums import CollectorType
from core.AsyncCoreLogger import AsyncCoreLogger
from core.DTOs.BatchStatusInfo import BatchStatusInfo
from core.DTOs.GetBatchLogsResponse import GetBatchLogsResponse
from core.DTOs.GetBatchStatusResponse import GetBatchStatusResponse
from core.enums import BatchStatus
from tests.helpers.patch_functions import block_sleep
from tests.test_automated.integration.api.conftest import disable_task_trigger


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
    bsr: GetBatchStatusResponse = ath.request_validator.get_batch_statuses(
        status=BatchStatus.IN_PROCESS
    )
    assert len(bsr.results) == 1
    bsi: BatchStatusInfo = bsr.results[0]

    assert bsi.id == batch_id
    assert bsi.strategy == CollectorType.EXAMPLE.value
    assert bsi.status == BatchStatus.IN_PROCESS

    # Release the barrier to resume execution
    barrier.release()
    await asyncio.sleep(0.1)

    csr: GetBatchStatusResponse = ath.request_validator.get_batch_statuses(
        collector_type=CollectorType.EXAMPLE,
        status=BatchStatus.READY_TO_LABEL
    )

    assert len(csr.results) == 1
    bsi: BatchStatusInfo = csr.results[0]

    assert bsi.id == batch_id
    assert bsi.strategy == CollectorType.EXAMPLE.value
    assert bsi.status == BatchStatus.READY_TO_LABEL

    bi: BatchInfo = ath.request_validator.get_batch_info(batch_id=batch_id)
    assert bi.status == BatchStatus.READY_TO_LABEL
    assert bi.total_url_count == 2
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

    await asyncio.sleep(0)

    bi: BatchInfo = ath.request_validator.get_batch_info(batch_id=batch_id)

    assert bi.status == BatchStatus.ERROR

    # Check there are logs
    assert not logger.log_queue.empty()
    await logger.flush_all()
    assert logger.log_queue.empty()

    gbl: GetBatchLogsResponse = ath.request_validator.get_batch_logs(batch_id=batch_id)
    assert gbl.logs[-1].log == "Error: Collector failed!"
    await logger.__aexit__(None, None, None)




