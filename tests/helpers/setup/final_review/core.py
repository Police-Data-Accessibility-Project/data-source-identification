from typing import Optional

from src.api.endpoints.annotate.agency.post.dto import URLAgencyAnnotationPostInfo
from src.core.enums import RecordType, SuggestedStatus
from tests.helpers.data_creator.core import DBDataCreator
from tests.helpers.setup.final_review.model import FinalReviewSetupInfo


async def setup_for_get_next_url_for_final_review(
        db_data_creator: DBDataCreator,
        annotation_count: Optional[int] = None,
        include_user_annotations: bool = True,
        include_miscellaneous_metadata: bool = True
) -> FinalReviewSetupInfo:
    """
    Sets up the database to test the final_review functions
    Auto-labels the URL with 'relevant=True' and 'record_type=ARREST_RECORDS'
    And applies auto-generated user annotations
    """

    batch_id = db_data_creator.batch()
    url_mapping = db_data_creator.urls(
        batch_id=batch_id,
        url_count=1
    ).url_mappings[0]
    if include_miscellaneous_metadata:
        await db_data_creator.url_miscellaneous_metadata(url_id=url_mapping.url_id)
    await db_data_creator.html_data([url_mapping.url_id])

    async def add_agency_suggestion() -> int:
        agency_id = await db_data_creator.agency()
        await db_data_creator.agency_user_suggestions(
            url_id=url_mapping.url_id,
            agency_annotation_info=URLAgencyAnnotationPostInfo(
                suggested_agency=agency_id
            )
        )
        return agency_id

    async def add_record_type_suggestion(record_type: RecordType):
        await db_data_creator.user_record_type_suggestion(
            url_id=url_mapping.url_id,
            record_type=record_type
        )

    async def add_relevant_suggestion(relevant: bool):
        await db_data_creator.user_relevant_suggestion(
            url_id=url_mapping.url_id,
            suggested_status=SuggestedStatus.RELEVANT if relevant else SuggestedStatus.NOT_RELEVANT
        )

    await db_data_creator.auto_relevant_suggestions(
        url_id=url_mapping.url_id,
        relevant=True
    )

    await db_data_creator.auto_record_type_suggestions(
        url_id=url_mapping.url_id,
        record_type=RecordType.ARREST_RECORDS
    )

    if include_user_annotations:
        await add_relevant_suggestion(False)
        await add_record_type_suggestion(RecordType.ACCIDENT_REPORTS)
        user_agency_id = await add_agency_suggestion()
    else:
        user_agency_id = None

    return FinalReviewSetupInfo(
        batch_id=batch_id,
        url_mapping=url_mapping,
        user_agency_id=user_agency_id
    )
