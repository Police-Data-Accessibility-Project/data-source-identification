import pytest

from src.core.enums import SuggestedStatus
from tests.helpers.complex_test_data_functions import setup_for_get_next_url_for_annotation
from tests.helpers.db_data_creator import DBDataCreator


@pytest.mark.asyncio
async def test_get_next_url_for_user_relevance_annotation_pending(
        db_data_creator: DBDataCreator
):
    """
    Users should receive a valid URL to annotate
    All users should receive the same next URL
    Once any user annotates that URL, none of the users should receive it again
    """
    setup_info = await setup_for_get_next_url_for_annotation(
        db_data_creator=db_data_creator,
        url_count=2
    )

    url_1 = setup_info.insert_urls_info.url_mappings[0]

    # Add `Relevancy` attribute with value `True`
    await db_data_creator.auto_relevant_suggestions(
        url_id=url_1.url_id,
        relevant=True
    )

    adb_client = db_data_creator.adb_client
    url_1 = await adb_client.get_next_url_for_relevance_annotation(
        user_id=1,
        batch_id=None
    )
    assert url_1 is not None

    url_2 = await adb_client.get_next_url_for_relevance_annotation(
        user_id=2,
        batch_id=None
    )
    assert url_2 is not None

    assert url_1.url_info.url == url_2.url_info.url

    # Annotate this URL, then check that the second URL is returned
    await adb_client.add_user_relevant_suggestion(
        url_id=url_1.url_info.url_id,
        user_id=1,
        suggested_status=SuggestedStatus.RELEVANT
    )

    url_3 = await adb_client.get_next_url_for_relevance_annotation(
        user_id=1,
        batch_id=None
    )
    assert url_3 is not None

    assert url_1 != url_3

    # Check that the second URL is also returned for another user
    url_4 = await adb_client.get_next_url_for_relevance_annotation(
        user_id=2,
        batch_id=None
    )
    assert url_4 is not None


    assert url_4 == url_3
