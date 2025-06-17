import pendulum
import pytest

from src.collectors.enums import CollectorType, URLStatus
from tests.helpers.batch_creation_parameters.core import TestBatchCreationParameters
from tests.helpers.batch_creation_parameters.url_creation_parameters import TestURLCreationParameters


@pytest.mark.asyncio
async def test_get_urls_aggregated_metrics(api_test_helper):
    ath = api_test_helper
    today = pendulum.parse('2021-01-01')

    batch_0_params = TestBatchCreationParameters(
        strategy=CollectorType.MANUAL,
        created_at=today.subtract(days=1),
        urls=[
            TestURLCreationParameters(
                count=1,
                status=URLStatus.PENDING,
            ),
        ]
    )
    batch_0 = await ath.db_data_creator.batch_v2(batch_0_params)
    oldest_url_id = batch_0.url_creation_infos[URLStatus.PENDING].url_mappings[0].url_id


    batch_1_params = TestBatchCreationParameters(
        strategy=CollectorType.MANUAL,
        urls=[
            TestURLCreationParameters(
                count=1,
                status=URLStatus.PENDING,
            ),
            TestURLCreationParameters(
                count=2,
                status=URLStatus.SUBMITTED
            ),
        ]
    )
    batch_1 = await ath.db_data_creator.batch_v2(batch_1_params)

    batch_2_params = TestBatchCreationParameters(
        strategy=CollectorType.AUTO_GOOGLER,
        urls=[
            TestURLCreationParameters(
                count=4,
                status=URLStatus.PENDING,
            ),
            TestURLCreationParameters(
                count=2,
                status=URLStatus.ERROR
            ),
            TestURLCreationParameters(
                count=1,
                status=URLStatus.VALIDATED
            ),
            TestURLCreationParameters(
                count=5,
                status=URLStatus.NOT_RELEVANT
            ),
        ]
    )
    batch_2 = await ath.db_data_creator.batch_v2(batch_2_params)

    dto = await ath.request_validator.get_urls_aggregated_metrics()

    assert dto.oldest_pending_url_id == oldest_url_id
    assert dto.oldest_pending_url_created_at == today.subtract(days=1).in_timezone('UTC').naive()
    assert dto.count_urls_pending == 6
    assert dto.count_urls_rejected == 5
    assert dto.count_urls_errors == 2
    assert dto.count_urls_validated == 1
    assert dto.count_urls_submitted == 2
    assert dto.count_urls_total == 16
