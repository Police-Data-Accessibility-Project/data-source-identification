import asyncio
import time

from collector_db.DTOs.BatchInfo import BatchInfo
from collector_db.DTOs.InsertURLsInfo import InsertURLsInfo
from collector_manager.DTOs.ExampleInputDTO import ExampleInputDTO
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

def test_get_batch_urls(api_test_helper):

    # Insert batch and urls into database
    ath = api_test_helper
    batch_id = ath.db_data_creator.batch()
    iui: InsertURLsInfo = ath.db_data_creator.urls(batch_id=batch_id, url_count=101)

    response = ath.request_validator.get_batch_urls(batch_id=batch_id, page=1)
    assert len(response.urls) == 100
    # Check that the first url corresponds to the first url inserted
    assert response.urls[0].url == iui.url_mappings[0].url
    # Check that the last url corresponds to the 100th url inserted
    assert response.urls[-1].url == iui.url_mappings[99].url


    # Check that a more limited set of urls exist
    response = ath.request_validator.get_batch_urls(batch_id=batch_id, page=2)
    assert len(response.urls) == 1
    # Check that this url corresponds to the last url inserted
    assert response.urls[0].url == iui.url_mappings[-1].url

def test_get_duplicate_urls(api_test_helper):

    # Insert batch and url into database
    ath = api_test_helper
    batch_id = ath.db_data_creator.batch()
    iui: InsertURLsInfo = ath.db_data_creator.urls(batch_id=batch_id, url_count=101)
    # Get a list of all url ids
    url_ids = [url.url_id for url in iui.url_mappings]

    # Create a second batch which will be associated with the duplicates
    dup_batch_id = ath.db_data_creator.batch()

    # Insert duplicate urls into database
    ath.db_data_creator.duplicate_urls(duplicate_batch_id=dup_batch_id, url_ids=url_ids)

    response = ath.request_validator.get_batch_url_duplicates(batch_id=dup_batch_id, page=1)
    assert len(response.duplicates) == 100

    response = ath.request_validator.get_batch_url_duplicates(batch_id=dup_batch_id, page=2)
    assert len(response.duplicates) == 1