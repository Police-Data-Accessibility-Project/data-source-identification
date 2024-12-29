import time

from collector_db.DTOs.BatchInfo import BatchInfo
from collector_manager.enums import CollectorType, CollectorStatus
from core.DTOs.BatchStatusInfo import BatchStatusInfo
from core.DTOs.CollectorStatusInfo import CollectorStatusInfo
from core.DTOs.CollectorStatusResponse import CollectorStatusResponse
from core.DTOs.GetBatchStatusResponse import GetBatchStatusResponse
from core.enums import BatchStatus


def test_example_collector(api_test_helper):
    ath = api_test_helper

    config = {
            "example_field": "example_value",
            "sleep_time": 1
        }

    data = ath.request_validator.post(
        url="/collector/example",
        json=config
    )
    batch_id = data["batch_id"]
    assert batch_id is not None
    assert data["message"] == "Started example_collector collector."

    bsr: GetBatchStatusResponse = ath.request_validator.get_batch_statuses()

    assert len(bsr.results) == 1
    bsi: BatchStatusInfo = bsr.results[0]

    assert bsi.id == batch_id
    assert bsi.strategy == CollectorType.EXAMPLE
    assert bsi.status == BatchStatus.IN_PROCESS

    time.sleep(2)

    csr: GetBatchStatusResponse = ath.request_validator.get_batch_statuses()

    assert len(csr.results) == 1
    bsi: BatchStatusInfo = csr.results[0]

    assert bsi.id == batch_id
    assert bsi.strategy == CollectorType.EXAMPLE
    assert bsi.status == BatchStatus.COMPLETE

    bi: BatchInfo = ath.request_validator.get_batch_info(batch_id=batch_id)
    assert bi.status == BatchStatus.COMPLETE
    assert bi.count == 2
    assert bi.parameters == config
    assert bi.strategy == "example_collector"



