from src.api.endpoints.review.dtos.approve import FinalReviewApprovalInfo
from src.core.enums import RecordType
from tests.helpers.db_data_creator import DBDataCreator, BatchURLCreationInfo


async def setup_validated_urls(db_data_creator: DBDataCreator) -> list[str]:
    creation_info: BatchURLCreationInfo = await db_data_creator.batch_and_urls(
        url_count=3,
        with_html_content=True
    )

    url_1 = creation_info.url_ids[0]
    url_2 = creation_info.url_ids[1]
    url_3 = creation_info.url_ids[2]
    await db_data_creator.adb_client.approve_url(
        approval_info=FinalReviewApprovalInfo(
            url_id=url_1,
            record_type=RecordType.ACCIDENT_REPORTS,
            agency_ids=[1, 2],
            name="URL 1 Name",
            description=None,
            record_formats=["Record Format 1", "Record Format 2"],
            data_portal_type="Data Portal Type 1",
            supplying_entity="Supplying Entity 1"
        ),
        user_id=1
    )
    await db_data_creator.adb_client.approve_url(
        approval_info=FinalReviewApprovalInfo(
            url_id=url_2,
            record_type=RecordType.INCARCERATION_RECORDS,
            agency_ids=[3, 4],
            name="URL 2 Name",
            description="URL 2 Description",
        ),
        user_id=2
    )
    await db_data_creator.adb_client.approve_url(
        approval_info=FinalReviewApprovalInfo(
            url_id=url_3,
            record_type=RecordType.ACCIDENT_REPORTS,
            agency_ids=[5, 6],
            name="URL 3 Name",
            description="URL 3 Description",
        ),
        user_id=3
    )
    return creation_info.urls
