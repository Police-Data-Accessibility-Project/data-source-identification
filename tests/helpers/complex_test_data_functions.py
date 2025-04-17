from typing import Optional

from pydantic import BaseModel

from collector_db.DTOs.InsertURLsInfo import InsertURLsInfo
from collector_db.DTOs.URLMapping import URLMapping
from collector_manager.enums import URLStatus
from core.enums import RecordType, SuggestionType
from tests.helpers.DBDataCreator import BatchURLCreationInfo
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

class AnnotateAgencySetupInfo(BaseModel):
    batch_id: int
    url_ids: list[int]

async def setup_for_annotate_agency(
        db_data_creator: DBDataCreator,
        url_count: int,
        suggestion_type: SuggestionType = SuggestionType.UNKNOWN,
        with_html_content: bool = True
):
    buci: BatchURLCreationInfo = await db_data_creator.batch_and_urls(
        url_count=url_count,
        with_html_content=with_html_content
    )
    await db_data_creator.auto_suggestions(
        url_ids=buci.url_ids,
        num_suggestions=1,
        suggestion_type=suggestion_type
    )

    return AnnotateAgencySetupInfo(batch_id=buci.batch_id, url_ids=buci.url_ids)

class FinalReviewSetupInfo(BaseModel):
    batch_id: int
    url_mapping: URLMapping

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
        await add_relevant_suggestion(1, False)
        await add_record_type_suggestion(1, RecordType.ACCIDENT_REPORTS)
        await add_agency_suggestion(1)

    return FinalReviewSetupInfo(
        batch_id=batch_id,
        url_mapping=url_mapping
    )
