from pydantic import BaseModel

from collector_db.DTOs.InsertURLsInfo import InsertURLsInfo
from collector_db.DTOs.URLMapping import URLMapping
from collector_manager.enums import URLStatus
from core.enums import RecordType
from tests.helpers.DBDataCreator import DBDataCreator

class AnnotationSetupInfo(BaseModel):
    batch_id: int
    insert_urls_info: InsertURLsInfo

async def setup_for_get_next_url_for_annotation(
        db_data_creator: DBDataCreator,
        url_count: int,
        outcome: URLStatus = URLStatus.PENDING
) -> AnnotationSetupInfo:
    batch_id = db_data_creator.batch()
    insert_urls_info = db_data_creator.urls(
        batch_id=batch_id,
        url_count=url_count,
        outcome=outcome
    )
    await db_data_creator.html_data(
        [
            url.url_id for url in insert_urls_info.url_mappings
        ]
    )
    return AnnotationSetupInfo(batch_id=batch_id, insert_urls_info=insert_urls_info)


class FinalReviewSetupInfo(BaseModel):
    batch_id: int
    url_mapping: URLMapping

async def setup_for_get_next_url_for_final_review(
        db_data_creator: DBDataCreator,
        annotation_count: int,
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

    async def add_agency_suggestion(count: int):
        agency_id = await db_data_creator.agency()
        for i in range(count):
            await db_data_creator.agency_user_suggestions(
                url_id=url_mapping.url_id,
                agency_id=agency_id
            )

    async def add_record_type_suggestion(count: int, record_type: RecordType):
        for i in range(count):
            await db_data_creator.user_record_type_suggestion(
                url_id=url_mapping.url_id,
                record_type=record_type
            )

    async def add_relevant_suggestion(count: int, relevant: bool):
        for i in range(count):
            await db_data_creator.user_relevant_suggestion(
                url_id=url_mapping.url_id,
                relevant=relevant
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
        await add_relevant_suggestion(annotation_count, True)
        await add_relevant_suggestion(1, False)
        await add_record_type_suggestion(3, RecordType.ARREST_RECORDS)
        await add_record_type_suggestion(2, RecordType.DISPATCH_RECORDINGS)
        await add_record_type_suggestion(1, RecordType.ACCIDENT_REPORTS)

    if include_user_annotations:
        # Add user suggestions for agencies, one suggested by 3 users, another by 2, another by 1
        for i in range(annotation_count):
            await add_agency_suggestion(i + 1)

    return FinalReviewSetupInfo(
        batch_id=batch_id,
        url_mapping=url_mapping
    )
