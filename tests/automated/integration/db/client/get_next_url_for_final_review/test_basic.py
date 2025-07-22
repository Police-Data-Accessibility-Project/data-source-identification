import pytest

from src.core.enums import SuggestedStatus, RecordType
from tests.helpers.setup.final_review.core import setup_for_get_next_url_for_final_review
from tests.helpers.db_data_creator import DBDataCreator


@pytest.mark.asyncio
async def test_get_next_url_for_final_review_basic(db_data_creator: DBDataCreator):
    """
    Test that an annotated URL is returned
    """

    setup_info = await setup_for_get_next_url_for_final_review(
        db_data_creator=db_data_creator,
        annotation_count=1,
        include_user_annotations=True
    )

    url_mapping = setup_info.url_mapping
    # Add agency auto suggestions
    await db_data_creator.agency_auto_suggestions(
        url_id=url_mapping.url_id,
        count=3
    )


    outer_result = await db_data_creator.adb_client.get_next_url_for_final_review(
        batch_id=None
    )
    result = outer_result.next_source

    assert result.url == url_mapping.url
    html_info = result.html_info
    assert html_info.description == "test description"
    assert html_info.title == "test html content"

    annotation_info = result.annotations
    relevant_info = annotation_info.relevant
    assert relevant_info.auto.is_relevant == True
    assert relevant_info.user == SuggestedStatus.NOT_RELEVANT

    record_type_info = annotation_info.record_type
    assert record_type_info.auto == RecordType.ARREST_RECORDS
    assert record_type_info.user == RecordType.ACCIDENT_REPORTS

    agency_info = annotation_info.agency
    auto_agency_suggestions = agency_info.auto
    assert auto_agency_suggestions.unknown == False
    assert len(auto_agency_suggestions.suggestions) == 3

    # Check user agency suggestion exists and is correct
    assert agency_info.user.pdap_agency_id == setup_info.user_agency_id
