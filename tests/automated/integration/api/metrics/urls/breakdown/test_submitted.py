import pendulum
import pytest

from src.collectors.enums import CollectorType, URLStatus
from tests.helpers.batch_creation_parameters.core import TestBatchCreationParameters
from tests.helpers.batch_creation_parameters.url_creation_parameters import TestURLCreationParameters


@pytest.mark.asyncio
async def test_get_urls_breakdown_submitted_metrics(api_test_helper):
    # Create URLs with submitted status, broken down in different amounts by different weeks
    # And ensure the URLs are
    today = pendulum.parse('2021-01-01')
    ath = api_test_helper

    batch_1_params = TestBatchCreationParameters(
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
        ]
    )
    batch_1 = await ath.db_data_creator.batch_v2(batch_1_params)
    batch_2_params = TestBatchCreationParameters(
        strategy=CollectorType.EXAMPLE,
        urls=[
            TestURLCreationParameters(
                count=3,
                status=URLStatus.SUBMITTED
            )
        ],
        created_at=today.subtract(weeks=1),
    )
    batch_2 = await ath.db_data_creator.batch_v2(batch_2_params)
    batch_3_params = TestBatchCreationParameters(
        strategy=CollectorType.AUTO_GOOGLER,
        created_at=today.subtract(weeks=1),
        urls=[
            TestURLCreationParameters(
                count=3,
                status=URLStatus.SUBMITTED
            ),
            TestURLCreationParameters(
                count=4,
                status=URLStatus.ERROR
            ),
            TestURLCreationParameters(
                count=5,
                status=URLStatus.VALIDATED
            ),
        ]
    )
    batch_3 = await ath.db_data_creator.batch_v2(batch_3_params)

    dto = await ath.request_validator.get_urls_breakdown_submitted_metrics()
    assert len(dto.entries) == 2

    entry_1 = dto.entries[0]
    assert entry_1.count_submitted == 6

    entry_2 = dto.entries[1]
    assert entry_2.count_submitted == 2
