import pytest

from src.core.enums import SuggestionType
from tests.helpers.complex_test_data_functions import setup_for_get_next_url_for_annotation
from tests.helpers.db_data_creator import DBDataCreator


@pytest.mark.asyncio
async def test_get_next_url_for_annotation_batch_filtering(
        db_data_creator: DBDataCreator
):
    """
    Test that for all annotation retrievals, batch filtering works as expected
    """
    setup_info_1 = await setup_for_get_next_url_for_annotation(
        db_data_creator=db_data_creator,
        url_count=1
    )
    setup_info_2 = await setup_for_get_next_url_for_annotation(
        db_data_creator=db_data_creator,
        url_count=3
    )

    def assert_batch_info(batch_info):
        assert batch_info.total_urls == 3
        assert batch_info.count_annotated == 0
        assert batch_info.count_not_annotated == 3

    url_1 = setup_info_1.insert_urls_info.url_mappings[0]
    url_2 = setup_info_2.insert_urls_info.url_mappings[0]

    # Test for relevance
    # If a batch id is provided, return first valid URL with that batch id
    result_with_batch_id = await db_data_creator.adb_client.get_next_url_for_relevance_annotation(
        user_id=1,
        batch_id=setup_info_2.batch_id
    )

    assert result_with_batch_id.url_info.url == url_2.url
    assert_batch_info(result_with_batch_id.batch_info)
    # If no batch id is provided, return first valid URL
    result_no_batch_id = await db_data_creator.adb_client.get_next_url_for_relevance_annotation(
        user_id=1,
        batch_id=None
    )

    assert result_no_batch_id.url_info.url == url_1.url

    # Test for record type
    # If a batch id is provided, return first valid URL with that batch id
    result_with_batch_id = await db_data_creator.adb_client.get_next_url_for_record_type_annotation(
        user_id=1,
        batch_id=setup_info_2.batch_id
    )

    assert result_with_batch_id.url_info.url == url_2.url
    assert_batch_info(result_with_batch_id.batch_info)

    # If no batch id is provided, return first valid URL
    result_no_batch_id = await db_data_creator.adb_client.get_next_url_for_record_type_annotation(
        user_id=1,
        batch_id=None
    )

    assert result_no_batch_id.url_info.url == url_1.url

    # Test for agency
    for url in [url_1, url_2]:
        await db_data_creator.auto_suggestions(
            url_ids=[url.url_id],
            num_suggestions=2,
            suggestion_type=SuggestionType.AUTO_SUGGESTION
        )

    # If a batch id is provided, return first valid URL with that batch id
    result_with_batch_id = await db_data_creator.adb_client.get_next_url_agency_for_annotation(
        user_id=1,
        batch_id=setup_info_2.batch_id
    )

    assert result_with_batch_id.next_annotation.url_info.url == url_2.url
    assert_batch_info(result_with_batch_id.next_annotation.batch_info)

    # If no batch id is provided, return first valid URL
    result_no_batch_id = await db_data_creator.adb_client.get_next_url_agency_for_annotation(
        user_id=1,
        batch_id=None
    )

    assert result_no_batch_id.next_annotation.url_info.url == url_1.url


    # All annotations
    result_with_batch_id = await db_data_creator.adb_client.get_next_url_for_all_annotations(
        batch_id=setup_info_2.batch_id
    )

    assert result_with_batch_id.next_annotation.url_info.url == url_2.url
    assert_batch_info(result_with_batch_id.next_annotation.batch_info)

    # If no batch id is provided, return first valid URL
    result_no_batch_id = await db_data_creator.adb_client.get_next_url_for_all_annotations(
        batch_id=None
    )

    assert result_no_batch_id.next_annotation.url_info.url == url_1.url
