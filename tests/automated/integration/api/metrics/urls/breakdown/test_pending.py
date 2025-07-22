import pendulum
import pytest

from src.api.endpoints.annotate.agency.post.dto import URLAgencyAnnotationPostInfo
from src.collectors.enums import CollectorType, URLStatus
from src.core.enums import SuggestedStatus, RecordType
from tests.helpers.batch_creation_parameters.annotation_info import AnnotationInfo
from tests.helpers.batch_creation_parameters.core import TestBatchCreationParameters
from tests.helpers.batch_creation_parameters.url_creation_parameters import TestURLCreationParameters


@pytest.mark.asyncio
async def test_get_urls_breakdown_pending_metrics(api_test_helper):
    # Build URLs, broken down into three separate weeks,
    # with each week having a different number of pending URLs
    # with a different number of kinds of annotations per URLs


    today = pendulum.parse('2021-01-01')
    ath = api_test_helper

    agency_id = await ath.db_data_creator.agency()
    # Additionally, add some URLs that are submitted,
    # validated, errored, and ensure they are not counted
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
    batch_2_params = TestBatchCreationParameters(
        strategy=CollectorType.EXAMPLE,
        urls=[
            TestURLCreationParameters(
                count=3,
                status=URLStatus.PENDING,
                annotation_info=AnnotationInfo(
                    user_relevant=SuggestedStatus.RELEVANT,
                    user_record_type=RecordType.CALLS_FOR_SERVICE
                )
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
                status=URLStatus.PENDING,
                annotation_info=AnnotationInfo(
                    user_relevant=SuggestedStatus.RELEVANT,
                    user_record_type=RecordType.INCARCERATION_RECORDS,
                    user_agency=URLAgencyAnnotationPostInfo(
                        suggested_agency=agency_id
                    )
                )
            ),
        ]
    )
    batch_3 = await ath.db_data_creator.batch_v2(batch_3_params)

    dto = await ath.request_validator.get_urls_breakdown_pending_metrics()
    assert len(dto.entries) == 2

    entry_1 = dto.entries[0]
    assert entry_1.count_pending_total == 8
    assert entry_1.count_pending_relevant_user == 8
    assert entry_1.count_pending_record_type_user == 8
    assert entry_1.count_pending_agency_user == 5

    entry_2 = dto.entries[1]
    assert entry_2.count_pending_total == 1
    assert entry_2.count_pending_relevant_user == 1
    assert entry_2.count_pending_record_type_user == 0
    assert entry_2.count_pending_agency_user == 0
