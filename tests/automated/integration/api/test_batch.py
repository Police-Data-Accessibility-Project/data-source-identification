import pytest

from src.db.dtos.batch import BatchInfo
from src.db.dtos.url.insert import InsertURLsInfo
from src.collectors.source_collectors.example.dtos.input import ExampleInputDTO
from src.collectors.enums import CollectorType, URLStatus
from src.core.enums import BatchStatus
from tests.helpers.batch_creation_parameters.url_creation_parameters import TestURLCreationParameters
from tests.helpers.batch_creation_parameters.core import TestBatchCreationParameters


@pytest.mark.asyncio
async def test_get_batch_summaries(api_test_helper):
    ath = api_test_helper

    batch_params = [
        TestBatchCreationParameters(
            urls=[
                TestURLCreationParameters(
                    count=1,
                    status=URLStatus.PENDING
                ),
                TestURLCreationParameters(
                    count=2,
                    status=URLStatus.SUBMITTED
                )
            ]
        ),
        TestBatchCreationParameters(
            urls=[
                TestURLCreationParameters(
                    count=4,
                    status=URLStatus.NOT_RELEVANT
                ),
                TestURLCreationParameters(
                    count=3,
                    status=URLStatus.ERROR
                )
            ]
        ),
        TestBatchCreationParameters(
            urls=[
                TestURLCreationParameters(
                    count=7,
                    status=URLStatus.DUPLICATE
                ),
                TestURLCreationParameters(
                    count=1,
                    status=URLStatus.SUBMITTED
                )
            ]
        )
    ]

    batch_1_creation_info = await ath.db_data_creator.batch_v2(batch_params[0])
    batch_2_creation_info = await ath.db_data_creator.batch_v2(batch_params[1])
    batch_3_creation_info = await ath.db_data_creator.batch_v2(batch_params[2])

    batch_1_id = batch_1_creation_info.batch_id
    batch_2_id = batch_2_creation_info.batch_id
    batch_3_id = batch_3_creation_info.batch_id


    response = ath.request_validator.get_batch_statuses()
    results = response.results

    assert len(results) == 3

    result_1 = results[0]
    assert result_1.id == batch_1_id
    assert result_1.status == BatchStatus.READY_TO_LABEL
    counts_1 = result_1.url_counts
    assert counts_1.total == 3
    assert counts_1.pending == 1
    assert counts_1.submitted == 2
    assert counts_1.not_relevant == 0
    assert counts_1.duplicate == 0
    assert counts_1.errored == 0

    result_2 = results[1]
    assert result_2.id == batch_2_id
    counts_2 = result_2.url_counts
    assert counts_2.total == 7
    assert counts_2.not_relevant == 4
    assert counts_2.errored == 3
    assert counts_2.pending == 0
    assert counts_2.submitted == 0
    assert counts_2.duplicate == 0

    result_3 = results[2]
    assert result_3.id == batch_3_id
    counts_3 = result_3.url_counts
    assert counts_3.total == 8
    assert counts_3.not_relevant == 0
    assert counts_3.errored == 0
    assert counts_3.pending == 0
    assert counts_3.submitted == 1
    assert counts_3.duplicate == 7






@pytest.mark.asyncio
async def test_get_batch_summaries_pending_url_filter(api_test_helper):
    ath = api_test_helper

    # Add an errored out batch
    batch_error = await ath.db_data_creator.batch_and_urls(
        strategy=CollectorType.EXAMPLE,
        url_count=2,
        batch_status=BatchStatus.ERROR
    )

    # Add a batch with pending urls
    batch_pending = await ath.db_data_creator.batch_and_urls(
        strategy=CollectorType.EXAMPLE,
        url_count=2,
        batch_status=BatchStatus.READY_TO_LABEL,
        with_html_content=True,
        url_status=URLStatus.PENDING
    )

    # Add a batch with submitted URLs
    batch_submitted = await ath.db_data_creator.batch_and_urls(
        strategy=CollectorType.EXAMPLE,
        url_count=2,
        batch_status=BatchStatus.READY_TO_LABEL,
        with_html_content=True,
        url_status=URLStatus.SUBMITTED
    )

    # Add an aborted batch
    batch_aborted = await ath.db_data_creator.batch_and_urls(
        strategy=CollectorType.EXAMPLE,
        url_count=2,
        batch_status=BatchStatus.ABORTED
    )

    # Add a batch with validated URLs
    batch_validated = await ath.db_data_creator.batch_and_urls(
        strategy=CollectorType.EXAMPLE,
        url_count=2,
        batch_status=BatchStatus.READY_TO_LABEL,
        with_html_content=True,
        url_status=URLStatus.VALIDATED
    )

    # Test filter for pending URLs and only retrieve the second batch
    pending_urls_results = ath.request_validator.get_batch_statuses(
        has_pending_urls=True
    )

    assert len(pending_urls_results.results) == 1
    assert pending_urls_results.results[0].id == batch_pending.batch_id

    # Test filter without pending URLs and retrieve the other four batches
    no_pending_urls_results = ath.request_validator.get_batch_statuses(
        has_pending_urls=False
    )

    assert len(no_pending_urls_results.results) == 4
    for result in no_pending_urls_results.results:
        assert result.id in [
            batch_error.batch_id,
            batch_submitted.batch_id,
            batch_validated.batch_id,
            batch_aborted.batch_id
        ]

    # Test no filter for pending URLs and retrieve all batches
    no_filter_results = ath.request_validator.get_batch_statuses()

    assert len(no_filter_results.results) == 5




def test_abort_batch(api_test_helper):
    ath = api_test_helper

    dto = ExampleInputDTO(
            sleep_time=1
        )

    batch_id = ath.request_validator.example_collector(dto=dto)["batch_id"]

    response = ath.request_validator.abort_batch(batch_id=batch_id)

    assert response.message == "Batch aborted."

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