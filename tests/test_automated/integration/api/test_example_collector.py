import time

from collector_db.DTOs.BatchInfo import BatchInfo
from collector_manager.DTOs.ExampleInputDTO import ExampleInputDTO
from collector_manager.enums import CollectorType
from core.DTOs.BatchStatusInfo import BatchStatusInfo
from core.DTOs.GetBatchLogsResponse import GetBatchLogsResponse
from core.DTOs.GetBatchStatusResponse import GetBatchStatusResponse
from core.enums import BatchStatus


def test_example_collector(api_test_helper):
    ath = api_test_helper

    dto = ExampleInputDTO(
            sleep_time=1
        )

    data = ath.request_validator.example_collector(
        dto=dto
    )
    batch_id = data["batch_id"]
    assert batch_id is not None
    assert data["message"] == "Started example_collector collector."

    bsr: GetBatchStatusResponse = ath.request_validator.get_batch_statuses(status=BatchStatus.IN_PROCESS)

    assert len(bsr.results) == 1
    bsi: BatchStatusInfo = bsr.results[0]

    assert bsi.id == batch_id
    assert bsi.strategy == CollectorType.EXAMPLE.value
    assert bsi.status == BatchStatus.IN_PROCESS

    time.sleep(2)

    csr: GetBatchStatusResponse = ath.request_validator.get_batch_statuses(collector_type=CollectorType.EXAMPLE, status=BatchStatus.COMPLETE)

    assert len(csr.results) == 1
    bsi: BatchStatusInfo = csr.results[0]

    assert bsi.id == batch_id
    assert bsi.strategy == CollectorType.EXAMPLE.value
    assert bsi.status == BatchStatus.COMPLETE

    bi: BatchInfo = ath.request_validator.get_batch_info(batch_id=batch_id)
    assert bi.status == BatchStatus.COMPLETE
    assert bi.total_url_count == 2
    assert bi.parameters == dto.model_dump()
    assert bi.strategy == "example_collector"
    assert bi.user_id == 1

    # Flush early to ensure logs are written
    ath.core.collector_manager.logger.flush_all()

    lr: GetBatchLogsResponse = ath.request_validator.get_batch_logs(batch_id=batch_id)


    assert len(lr.logs) > 0



