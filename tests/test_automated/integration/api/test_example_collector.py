import time
from unittest.mock import MagicMock

from collector_db.DTOs.BatchInfo import BatchInfo
from collector_manager.DTOs.ExampleInputDTO import ExampleInputDTO
from collector_manager.ExampleCollector import ExampleCollector
from collector_manager.enums import CollectorType
from core.DTOs.BatchStatusInfo import BatchStatusInfo
from core.DTOs.GetBatchLogsResponse import GetBatchLogsResponse
from core.DTOs.GetBatchStatusResponse import GetBatchStatusResponse
from core.enums import BatchStatus
from tests.test_automated.integration.api.conftest import disable_task_trigger


def test_example_collector(api_test_helper):
    ath = api_test_helper

    # Temporarily disable task trigger
    disable_task_trigger(ath)

    dto = ExampleInputDTO(
            sleep_time=1
        )

    data = ath.request_validator.example_collector(
        dto=dto
    )
    batch_id = data["batch_id"]
    assert batch_id is not None
    assert data["message"] == "Started example collector."

    bsr: GetBatchStatusResponse = ath.request_validator.get_batch_statuses(
        status=BatchStatus.IN_PROCESS
    )

    assert len(bsr.results) == 1
    bsi: BatchStatusInfo = bsr.results[0]

    assert bsi.id == batch_id
    assert bsi.strategy == CollectorType.EXAMPLE.value
    assert bsi.status == BatchStatus.IN_PROCESS

    time.sleep(2)

    csr: GetBatchStatusResponse = ath.request_validator.get_batch_statuses(
        collector_type=CollectorType.EXAMPLE,
        status=BatchStatus.COMPLETE
    )

    assert len(csr.results) == 1
    bsi: BatchStatusInfo = csr.results[0]

    assert bsi.id == batch_id
    assert bsi.strategy == CollectorType.EXAMPLE.value
    assert bsi.status == BatchStatus.COMPLETE

    bi: BatchInfo = ath.request_validator.get_batch_info(batch_id=batch_id)
    assert bi.status == BatchStatus.COMPLETE
    assert bi.total_url_count == 2
    assert bi.parameters == dto.model_dump()
    assert bi.strategy == CollectorType.EXAMPLE.value
    assert bi.user_id is not None

    # Flush early to ensure logs are written
    # Commented out due to inconsistency in execution
    # ath.core.core_logger.flush_all()
    #
    # time.sleep(10)
    #
    # lr: GetBatchLogsResponse = ath.request_validator.get_batch_logs(batch_id=batch_id)
    #
    # assert len(lr.logs) > 0

    # Check that task was triggered
    ath.async_core.collector_manager.\
        post_collection_function_trigger.\
        trigger_or_rerun.assert_called_once()


def test_example_collector_error(api_test_helper, monkeypatch):
    """
    Test that when an error occurs in a collector, the batch is properly update
    """
    ath = api_test_helper

    # Patch the collector to raise an exception during run_implementation
    mock = MagicMock()
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

    time.sleep(1)

    bi: BatchInfo = ath.request_validator.get_batch_info(batch_id=batch_id)

    assert bi.status == BatchStatus.ERROR

    #
    # ath.core.core_logger.flush_all()
    #
    # time.sleep(10)
    #
    # gbl: GetBatchLogsResponse = ath.request_validator.get_batch_logs(batch_id=batch_id)
    # assert gbl.logs[-1].log == "Error: Collector failed!"
    #
    #


