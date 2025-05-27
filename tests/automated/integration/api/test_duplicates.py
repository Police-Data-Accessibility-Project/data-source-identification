import pytest

from src.db.DTOs.BatchInfo import BatchInfo
from src.collector_manager.DTOs.ExampleInputDTO import ExampleInputDTO
from tests.automated.integration.api.conftest import disable_task_trigger


@pytest.mark.asyncio
async def test_duplicates(api_test_helper):
    ath = api_test_helper

    # Temporarily disable task trigger
    disable_task_trigger(ath)

    dto = ExampleInputDTO(
            sleep_time=0
        )

    batch_id_1 = ath.request_validator.example_collector(
        dto=dto
    )["batch_id"]

    assert batch_id_1 is not None

    batch_id_2 = ath.request_validator.example_collector(
        dto=dto
    )["batch_id"]

    assert batch_id_2 is not None

    await ath.wait_for_all_batches_to_complete()


    bi_1: BatchInfo = ath.request_validator.get_batch_info(batch_id_1)
    bi_2: BatchInfo = ath.request_validator.get_batch_info(batch_id_2)

    bi_1.total_url_count = 2
    bi_2.total_url_count = 0
    bi_1.duplicate_url_count = 0
    bi_2.duplicate_url_count = 2

    url_info_1 = ath.request_validator.get_batch_urls(batch_id_1)
    url_info_2 = ath.request_validator.get_batch_urls(batch_id_2)

    assert len(url_info_1.urls) == 2
    assert len(url_info_2.urls) == 0

    dup_info_1 = ath.request_validator.get_batch_url_duplicates(batch_id_1)
    dup_info_2 = ath.request_validator.get_batch_url_duplicates(batch_id_2)

    assert len(dup_info_1.duplicates) == 0
    assert len(dup_info_2.duplicates) == 2

    assert dup_info_2.duplicates[0].original_url_id == url_info_1.urls[0].id
    assert dup_info_2.duplicates[1].original_url_id == url_info_1.urls[1].id

    assert dup_info_2.duplicates[0].original_batch_id == batch_id_1
    assert dup_info_2.duplicates[1].original_batch_id == batch_id_1




