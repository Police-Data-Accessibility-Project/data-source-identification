import pytest

from src.core.enums import SuggestionType
from tests.helpers.setup.final_review.core import setup_for_get_next_url_for_final_review
from tests.helpers.data_creator.core import DBDataCreator


@pytest.mark.asyncio
async def test_get_next_url_for_final_review_favor_more_components(db_data_creator: DBDataCreator):
    """
    Test in the case of two URLs, favoring the one with more annotations for more components
    i.e., if one has annotations for record type and agency id, that should be favored over one with just record type
    """

    setup_info_without_user_anno = await setup_for_get_next_url_for_final_review(
        db_data_creator=db_data_creator,
        annotation_count=3,
        include_user_annotations=False
    )
    url_mapping_without_user_anno = setup_info_without_user_anno.url_mapping

    setup_info_with_user_anno = await setup_for_get_next_url_for_final_review(
        db_data_creator=db_data_creator,
        annotation_count=3,
        include_user_annotations=True
    )
    url_mapping_with_user_anno = setup_info_with_user_anno.url_mapping

    # Have both be listed as unknown

    for url_mapping in [url_mapping_with_user_anno, url_mapping_without_user_anno]:
        await db_data_creator.agency_auto_suggestions(
            url_id=url_mapping.url_id,
            count=3,
            suggestion_type=SuggestionType.UNKNOWN
        )

    result = await db_data_creator.adb_client.get_next_url_for_final_review(
        batch_id=None
    )

    assert result.next_source.id == url_mapping_with_user_anno.url_id
