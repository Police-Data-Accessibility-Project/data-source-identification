import pytest

from src.core.enums import SuggestedStatus
from src.db.dtos.url.mapping import URLMapping
from tests.helpers.complex_test_data_functions import setup_for_get_next_url_for_annotation
from tests.helpers.db_data_creator import DBDataCreator


@pytest.mark.asyncio
async def test_annotate_url_marked_not_relevant(db_data_creator: DBDataCreator):
    """
    If a URL is marked not relevant by the user, they should not receive that URL
    in calls to get an annotation for record type or agency
    Other users should still receive the URL
    """
    setup_info = await setup_for_get_next_url_for_annotation(
        db_data_creator=db_data_creator,
        url_count=2
    )
    adb_client = db_data_creator.adb_client
    url_to_mark_not_relevant: URLMapping = setup_info.insert_urls_info.url_mappings[0]
    url_to_mark_relevant: URLMapping = setup_info.insert_urls_info.url_mappings[1]
    for url_mapping in setup_info.insert_urls_info.url_mappings:
        await db_data_creator.agency_auto_suggestions(
            url_id=url_mapping.url_id,
            count=3
        )
    await adb_client.add_user_relevant_suggestion(
        user_id=1,
        url_id=url_to_mark_not_relevant.url_id,
        suggested_status=SuggestedStatus.NOT_RELEVANT
    )
    await adb_client.add_user_relevant_suggestion(
        user_id=1,
        url_id=url_to_mark_relevant.url_id,
        suggested_status=SuggestedStatus.RELEVANT
    )

    # User should not receive the URL for record type annotation
    record_type_annotation_info = await adb_client.get_next_url_for_record_type_annotation(
        user_id=1,
        batch_id=None
    )
    assert record_type_annotation_info.url_info.url_id != url_to_mark_not_relevant.url_id

    # Other users also should not receive the URL for record type annotation
    record_type_annotation_info = await adb_client.get_next_url_for_record_type_annotation(
        user_id=2,
        batch_id=None
    )
    assert record_type_annotation_info.url_info.url_id != \
           url_to_mark_not_relevant.url_id, "Other users should not receive the URL for record type annotation"

    # User should not receive the URL for agency annotation
    agency_annotation_info_user_1 = await adb_client.get_next_url_agency_for_annotation(
        user_id=1,
        batch_id=None
    )
    assert agency_annotation_info_user_1.next_annotation.url_info.url_id != url_to_mark_not_relevant.url_id

    # Other users also should not receive the URL for agency annotation
    agency_annotation_info_user_2 = await adb_client.get_next_url_agency_for_annotation(
        user_id=2,
        batch_id=None
    )
    assert agency_annotation_info_user_1.next_annotation.url_info.url_id != url_to_mark_not_relevant.url_id
