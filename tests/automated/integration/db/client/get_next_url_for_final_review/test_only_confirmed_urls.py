import pytest

from src.collectors.enums import URLStatus
from tests.helpers.db_data_creator import DBDataCreator


@pytest.mark.asyncio
async def test_get_next_url_for_final_review_only_confirmed_urls(db_data_creator: DBDataCreator):
    """
    Test in the case of one URL that is submitted
    Should not be returned.
    """
    batch_id = db_data_creator.batch()
    url_mapping = db_data_creator.urls(
        batch_id=batch_id,
        url_count=1,
        outcome=URLStatus.SUBMITTED
    ).url_mappings[0]

    result = await db_data_creator.adb_client.get_next_url_for_final_review(
        batch_id=None
    )

    assert result is None
