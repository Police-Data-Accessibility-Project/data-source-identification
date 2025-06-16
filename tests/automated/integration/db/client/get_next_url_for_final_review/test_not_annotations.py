import pytest

from tests.helpers.db_data_creator import DBDataCreator


@pytest.mark.asyncio
async def test_get_next_url_for_final_review_no_annotations(db_data_creator: DBDataCreator):
    """
    Test in the case of one URL with no annotations.
    No annotations should be returned
    """
    batch_id = db_data_creator.batch()
    url_mapping = db_data_creator.urls(batch_id=batch_id, url_count=1).url_mappings[0]

    result = await db_data_creator.adb_client.get_next_url_for_final_review(
        batch_id=None
    )

    assert result is None
