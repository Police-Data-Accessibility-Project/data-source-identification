import pytest

from src.api.endpoints.annotate.agency.post.dto import URLAgencyAnnotationPostInfo
from src.core.enums import SuggestedStatus, RecordType
from tests.helpers.batch_creation_parameters.annotation_info import AnnotationInfo
from tests.helpers.batch_creation_parameters.core import TestBatchCreationParameters
from tests.helpers.batch_creation_parameters.url_creation_parameters import TestURLCreationParameters


def create_batch(
    annotation_info: AnnotationInfo = AnnotationInfo(),
    count: int = 1,
):
    return TestBatchCreationParameters(
        urls=[
            TestURLCreationParameters(
                count=count,
                annotation_info=annotation_info,
            )
        ]
    )



async def setup_test_batches(db_data_creator):
    batches = [
        create_batch(
            annotation_info=AnnotationInfo(
                user_relevant=SuggestedStatus.NOT_RELEVANT
            )
        ),
        create_batch(
            annotation_info=AnnotationInfo(
                user_relevant=SuggestedStatus.RELEVANT,
                user_record_type=RecordType.ARREST_RECORDS
            ),
            count=2
        ),
        create_batch(
            annotation_info=AnnotationInfo(
                user_relevant=SuggestedStatus.RELEVANT,
                user_record_type=RecordType.CALLS_FOR_SERVICE,
                user_agency=URLAgencyAnnotationPostInfo(
                    suggested_agency=await db_data_creator.agency()
                )
            ),
            count=3
        ),
        create_batch(
            annotation_info=AnnotationInfo(
                user_agency=URLAgencyAnnotationPostInfo(
                    is_new=True
                )
            ),
            count=1
        ),
        create_batch(
            count=5
        ),
        create_batch(
            annotation_info=AnnotationInfo(
                user_relevant=SuggestedStatus.NOT_RELEVANT,
                user_record_type=RecordType.PERSONNEL_RECORDS,
                user_agency=URLAgencyAnnotationPostInfo(
                    suggested_agency=await db_data_creator.agency()
                )
            ),
            count=2
        ),
        create_batch(
            annotation_info=AnnotationInfo(
                user_relevant=SuggestedStatus.RELEVANT,
                user_agency=URLAgencyAnnotationPostInfo(
                    is_new=True
                )
            ),
            count=3
        ),
        create_batch(
            annotation_info=AnnotationInfo(
                user_record_type=RecordType.BOOKING_REPORTS,
            ),
            count=2
        ),
        create_batch(
            count=2
        )
    ]

    for batch in batches:
        await db_data_creator.batch_v2(batch)

@pytest.mark.asyncio
async def test_get_urls_aggregated_pending_metrics(api_test_helper):
    ath = api_test_helper
    db_data_creator = ath.db_data_creator
    await setup_test_batches(db_data_creator)

    response = await ath.request_validator.get_urls_aggregated_pending_metrics()
    r = response
    assert r.all == 21
    assert r.relevant == 11
    assert r.record_type == 9
    assert r.agency == 9
    assert r.annotations_0 == 7
    assert r.annotations_1 == 4
    assert r.annotations_2 == 5
    assert r.annotations_3 == 5



