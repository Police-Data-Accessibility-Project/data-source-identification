import pendulum
import pytest

from src.collectors.enums import CollectorType, URLStatus
from src.core.enums import BatchStatus
from tests.helpers.batch_creation_parameters.core import TestBatchCreationParameters
from tests.helpers.batch_creation_parameters.url_creation_parameters import TestURLCreationParameters


@pytest.mark.asyncio
async def test_get_batches_breakdown_metrics(api_test_helper):
    # Create a different batch for each month, with different URLs
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
        outcome=BatchStatus.ERROR,
        created_at=today.subtract(weeks=1),
    )
    batch_2 = await ath.db_data_creator.batch_v2(batch_2_params)
    batch_3_params = TestBatchCreationParameters(
        strategy=CollectorType.AUTO_GOOGLER,
        created_at=today.subtract(weeks=2),
        urls=[
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
            ),
        ]
    )
    batch_3 = await ath.db_data_creator.batch_v2(batch_3_params)

    dto_1 = await ath.request_validator.get_batches_breakdown_metrics(
        page=1
    )
    assert len(dto_1.batches) == 3
    dto_batch_1 = dto_1.batches[2]
    assert dto_batch_1.batch_id == batch_1.batch_id
    assert dto_batch_1.strategy == CollectorType.MANUAL
    assert dto_batch_1.status == BatchStatus.READY_TO_LABEL
    assert pendulum.instance(dto_batch_1.created_at) > today
    assert dto_batch_1.count_url_total == 3
    assert dto_batch_1.count_url_pending == 1
    assert dto_batch_1.count_url_submitted == 2
    assert dto_batch_1.count_url_rejected == 0
    assert dto_batch_1.count_url_error == 0
    assert dto_batch_1.count_url_validated == 0

    dto_batch_2 = dto_1.batches[1]
    assert dto_batch_2.batch_id == batch_2.batch_id
    assert dto_batch_2.status == BatchStatus.ERROR
    assert dto_batch_2.strategy == CollectorType.EXAMPLE
    assert pendulum.instance(dto_batch_2.created_at) == today.subtract(weeks=1)
    assert dto_batch_2.count_url_total == 0
    assert dto_batch_2.count_url_submitted == 0
    assert dto_batch_2.count_url_pending == 0
    assert dto_batch_2.count_url_rejected == 0
    assert dto_batch_2.count_url_error == 0
    assert dto_batch_2.count_url_validated == 0

    dto_batch_3 = dto_1.batches[0]
    assert dto_batch_3.batch_id == batch_3.batch_id
    assert dto_batch_3.status == BatchStatus.READY_TO_LABEL
    assert dto_batch_3.strategy == CollectorType.AUTO_GOOGLER
    assert pendulum.instance(dto_batch_3.created_at) == today.subtract(weeks=2)
    assert dto_batch_3.count_url_total == 12
    assert dto_batch_3.count_url_pending == 0
    assert dto_batch_3.count_url_submitted == 0
    assert dto_batch_3.count_url_rejected == 3
    assert dto_batch_3.count_url_error == 4
    assert dto_batch_3.count_url_validated == 5

    dto_2 = await ath.request_validator.get_batches_breakdown_metrics(
        page=2
    )
    assert len(dto_2.batches) == 0
