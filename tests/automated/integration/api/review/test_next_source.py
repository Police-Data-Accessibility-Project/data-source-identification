import pytest

from src.core.enums import SuggestedStatus, RecordType
from tests.helpers.complex_test_data_functions import setup_for_get_next_url_for_final_review


@pytest.mark.asyncio
async def test_review_next_source(api_test_helper):
    ath = api_test_helper

    setup_info = await setup_for_get_next_url_for_final_review(
        db_data_creator=ath.db_data_creator,
        include_user_annotations=True
    )
    url_mapping = setup_info.url_mapping

    await ath.db_data_creator.agency_auto_suggestions(
        url_id=url_mapping.url_id,
        count=3
    )
    confirmed_agency_id = await ath.db_data_creator.agency_confirmed_suggestion(url_id=url_mapping.url_id)

    outer_result = await ath.request_validator.review_next_source()

    result = outer_result.next_source

    assert result.name == "Test Name"
    assert result.description == "Test Description"

    optional_metadata = result.optional_metadata

    assert optional_metadata.data_portal_type == "Test Data Portal Type"
    assert optional_metadata.supplying_entity == "Test Supplying Entity"
    assert optional_metadata.record_formats == ["Test Record Format", "Test Record Format 2"]

    assert result.url == url_mapping.url
    html_info = result.html_info
    assert html_info.description == "test description"
    assert html_info.title == "test html content"

    annotation_info = result.annotations
    relevant_info = annotation_info.relevant
    assert relevant_info.auto == True
    assert relevant_info.user == SuggestedStatus.NOT_RELEVANT

    record_type_info = annotation_info.record_type
    assert record_type_info.auto == RecordType.ARREST_RECORDS
    assert record_type_info.user == RecordType.ACCIDENT_REPORTS

    agency_info = annotation_info.agency
    auto_agency_suggestions = agency_info.auto
    assert auto_agency_suggestions.unknown == False
    assert len(auto_agency_suggestions.suggestions) == 3

    # Check user agency suggestions exist and in descending order of count
    user_agency_suggestion = agency_info.user
    assert user_agency_suggestion.pdap_agency_id == setup_info.user_agency_id


    # Check confirmed agencies exist
    confirmed_agencies = agency_info.confirmed
    assert len(confirmed_agencies) == 1
    confirmed_agency = confirmed_agencies[0]
    assert confirmed_agency.pdap_agency_id == confirmed_agency_id
