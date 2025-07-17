import pytest

from src.core.enums import RecordType
from tests.helpers.setup.annotation.core import setup_for_get_next_url_for_annotation
from tests.helpers.db_data_creator import DBDataCreator


@pytest.mark.asyncio
async def test_get_next_url_for_user_record_type_annotation(db_data_creator: DBDataCreator):
    """
    All users should receive the same next valid URL for record type annotation
    Once any user annotates that URL, none of the users should receive it
    """
    setup_info = await setup_for_get_next_url_for_annotation(
        db_data_creator,
        url_count=2
    )

    # All users should receive the same URL
    url_1 = setup_info.insert_urls_info.url_mappings[0]
    url_2 = setup_info.insert_urls_info.url_mappings[1]

    adb_client = db_data_creator.adb_client

    url_user_1 = await adb_client.get_next_url_for_record_type_annotation(
        user_id=1,
        batch_id=None
    )
    assert url_user_1 is not None

    url_user_2 = await adb_client.get_next_url_for_record_type_annotation(
        user_id=2,
        batch_id=None
    )

    assert url_user_2 is not None

    # Check that the URLs are the same
    assert url_user_1 == url_user_2

    # After annotating, both users should receive a different URL
    await adb_client.add_user_record_type_suggestion(
        user_id=1,
        url_id=url_1.url_id,
        record_type=RecordType.ARREST_RECORDS
    )

    next_url_user_1 = await adb_client.get_next_url_for_record_type_annotation(
        user_id=1,
        batch_id=None
    )

    next_url_user_2 = await adb_client.get_next_url_for_record_type_annotation(
        user_id=2,
        batch_id=None
    )

    assert next_url_user_1 != url_user_1
    assert next_url_user_1 == next_url_user_2
