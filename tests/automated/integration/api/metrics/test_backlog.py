import pendulum
import pytest

from src.collectors.enums import CollectorType, URLStatus
from src.core.enums import SuggestedStatus
from tests.helpers.batch_creation_parameters.annotation_info import AnnotationInfo
from tests.helpers.batch_creation_parameters.core import TestBatchCreationParameters
from tests.helpers.batch_creation_parameters.url_creation_parameters import TestURLCreationParameters


@pytest.mark.asyncio
async def test_get_backlog_metrics(api_test_helper):
    today = pendulum.parse('2021-01-01')

    ath = api_test_helper
    adb_client = ath.adb_client()


    # Populate the backlog table and test that backlog metrics returned on a monthly basis
    # Ensure that multiple days in each month are added to the backlog table, with different values


    batch_1_params = TestBatchCreationParameters(
        strategy=CollectorType.MANUAL,
        urls=[
            TestURLCreationParameters(
                count=1,
                status=URLStatus.PENDING,
                annotation_info=AnnotationInfo(
                    user_relevant=SuggestedStatus.NOT_RELEVANT
                )
            ),
            TestURLCreationParameters(
                count=2,
                status=URLStatus.SUBMITTED
            ),
        ]
    )
    batch_1 = await ath.db_data_creator.batch_v2(batch_1_params)

    await adb_client.populate_backlog_snapshot(
        dt=today.subtract(months=3).naive()
    )

    await adb_client.populate_backlog_snapshot(
        dt=today.subtract(months=2, days=3).naive()
    )

    batch_2_params = TestBatchCreationParameters(
        strategy=CollectorType.AUTO_GOOGLER,
        urls=[
            TestURLCreationParameters(
                count=4,
                status=URLStatus.PENDING,
                annotation_info=AnnotationInfo(
                    user_relevant=SuggestedStatus.NOT_RELEVANT
                )
            ),
            TestURLCreationParameters(
                count=2,
                status=URLStatus.ERROR
            ),
        ]
    )
    batch_2 = await ath.db_data_creator.batch_v2(batch_2_params)

    await adb_client.populate_backlog_snapshot(
        dt=today.subtract(months=2).naive()
    )

    await adb_client.populate_backlog_snapshot(
        dt=today.subtract(months=1, days=4).naive()
    )

    batch_3_params = TestBatchCreationParameters(
        strategy=CollectorType.AUTO_GOOGLER,
        urls=[
            TestURLCreationParameters(
                count=7,
                status=URLStatus.PENDING,
                annotation_info=AnnotationInfo(
                    user_relevant=SuggestedStatus.NOT_RELEVANT
                )
            ),
            TestURLCreationParameters(
                count=5,
                status=URLStatus.VALIDATED
            ),
        ]
    )
    batch_3 = await ath.db_data_creator.batch_v2(batch_3_params)

    await adb_client.populate_backlog_snapshot(
        dt=today.subtract(months=1).naive()
    )

    dto = await ath.request_validator.get_backlog_metrics()

    assert len(dto.entries) == 3

    # Test that the count closest to the beginning of the month is returned for each month
    assert dto.entries[0].count_pending_total == 1
    assert dto.entries[1].count_pending_total == 5
    assert dto.entries[2].count_pending_total == 12
