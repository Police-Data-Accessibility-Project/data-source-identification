import pytest

from src.collectors.enums import CollectorType, URLStatus
from src.core.enums import BatchStatus
from tests.helpers.batch_creation_parameters.core import TestBatchCreationParameters
from tests.helpers.batch_creation_parameters.url_creation_parameters import TestURLCreationParameters


@pytest.mark.asyncio
async def test_get_batches_aggregated_metrics(api_test_helper):
    ath = api_test_helper
    # Create successful batches with URLs of different statuses
    all_params = []
    for i in range(3):
        params = TestBatchCreationParameters(
            strategy=CollectorType.MANUAL,
            urls=[
                TestURLCreationParameters(
                    count=1,
                    status=URLStatus.PENDING
                ),
                TestURLCreationParameters(
                    count=2,
                    status=URLStatus.SUBMITTED
                ),
                TestURLCreationParameters(
                    count=3,
                    status=URLStatus.NOT_RELEVANT
                ),
                TestURLCreationParameters(
                    count=4,
                    status=URLStatus.ERROR
                ),
                TestURLCreationParameters(
                    count=5,
                    status=URLStatus.VALIDATED
                )
            ]
        )
        all_params.append(params)


    # Create failed batches
    for i in range(2):
        params = TestBatchCreationParameters(
            outcome=BatchStatus.ERROR
        )
        all_params.append(params)

    for params in all_params:
        await ath.db_data_creator.batch_v2(params)

    dto = await ath.request_validator.get_batches_aggregated_metrics()
    assert dto.total_batches == 5
    inner_dto_example = dto.by_strategy[CollectorType.EXAMPLE]
    assert inner_dto_example.count_urls == 0
    assert inner_dto_example.count_successful_batches == 0
    assert inner_dto_example.count_failed_batches == 2
    assert inner_dto_example.count_urls_pending == 0
    assert inner_dto_example.count_urls_submitted == 0
    assert inner_dto_example.count_urls_rejected == 0
    assert inner_dto_example.count_urls_errors == 0
    assert inner_dto_example.count_urls_validated == 0

    inner_dto_manual = dto.by_strategy[CollectorType.MANUAL]
    assert inner_dto_manual.count_urls == 45
    assert inner_dto_manual.count_successful_batches == 3
    assert inner_dto_manual.count_failed_batches == 0
    assert inner_dto_manual.count_urls_pending == 3
    assert inner_dto_manual.count_urls_submitted == 6
    assert inner_dto_manual.count_urls_rejected == 9
    assert inner_dto_manual.count_urls_errors == 12
    assert inner_dto_manual.count_urls_validated == 15
