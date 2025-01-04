import time

from collector_db.DTOs.BatchInfo import BatchInfo
from collector_manager.DTOs.ExampleInputDTO import ExampleInputDTO
from core.DTOs.GetBatchStatusResponse import GetBatchStatusResponse
from core.enums import BatchStatus


def test_abort_batch(api_test_helper):
    ath = api_test_helper

    dto = ExampleInputDTO(
            sleep_time=1
        )

    batch_id = ath.request_validator.example_collector(dto=dto)["batch_id"]

    response = ath.request_validator.abort_batch(batch_id=batch_id)

    assert response.message == "Batch aborted."

    time.sleep(3)

    bi: BatchInfo = ath.request_validator.get_batch_info(batch_id=batch_id)

    assert bi.status == BatchStatus.ABORTED

