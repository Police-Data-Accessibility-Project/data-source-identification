import pytest

from tests.helpers.complex_test_data_functions import setup_for_annotate_agency
from tests.helpers.db_data_creator import DBDataCreator


@pytest.mark.asyncio
async def test_get_next_url_for_user_agency_annotation(db_data_creator: DBDataCreator):
    """
    All users should receive the same next valid URL for agency annotation
    Once any user annotates that URL, none of the users should receive it
    """
    setup_info = await setup_for_annotate_agency(
        db_data_creator,
        url_count=2
    )

    # All users should receive the same URL
    url_1 = setup_info.url_ids[0]
    url_2 = setup_info.url_ids[1]

    adb_client = db_data_creator.adb_client
    url_user_1 = await adb_client.get_next_url_agency_for_annotation(
        user_id=1,
        batch_id=None
    )
    assert url_user_1 is not None

    url_user_2 = await adb_client.get_next_url_agency_for_annotation(
        user_id=2,
        batch_id=None
    )

    assert url_user_2 is not None

    # Check that the URLs are the same
    assert url_user_1 == url_user_2

    # Annotate the URL
    await adb_client.add_agency_manual_suggestion(
        url_id=url_1,
        user_id=1,
        is_new=True,
        agency_id=None
    )

    # Both users should receive the next URL
    next_url_user_1 = await adb_client.get_next_url_agency_for_annotation(
        user_id=1,
        batch_id=None
    )
    assert next_url_user_1 is not None

    next_url_user_2 = await adb_client.get_next_url_agency_for_annotation(
        user_id=2,
        batch_id=None
    )
    assert next_url_user_2 is not None

    assert url_user_1 != next_url_user_1
    assert next_url_user_1 == next_url_user_2
