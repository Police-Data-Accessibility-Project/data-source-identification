import pytest

from tests.helpers.complex_test_data_functions import setup_for_get_next_url_for_final_review
from tests.helpers.db_data_creator import DBDataCreator


@pytest.mark.asyncio
async def test_get_next_url_for_final_review_batch_id_filtering(db_data_creator: DBDataCreator):
    setup_info_1 = await setup_for_get_next_url_for_final_review(
        db_data_creator=db_data_creator,
        annotation_count=3,
        include_user_annotations=True
    )

    setup_info_2 = await setup_for_get_next_url_for_final_review(
        db_data_creator=db_data_creator,
        annotation_count=3,
        include_user_annotations=True
    )

    url_mapping_1 = setup_info_1.url_mapping
    url_mapping_2 = setup_info_2.url_mapping

    # If a batch id is provided, return first valid URL with that batch id
    result_with_batch_id =await db_data_creator.adb_client.get_next_url_for_final_review(
        batch_id=setup_info_2.batch_id
    )

    assert result_with_batch_id.url == url_mapping_2.url

    # If no batch id is provided, return first valid URL
    result_no_batch_id =await db_data_creator.adb_client.get_next_url_for_final_review(
        batch_id=None
    )

    assert result_no_batch_id.url == url_mapping_1.url
