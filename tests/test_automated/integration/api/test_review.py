import pytest

from core.enums import RecordType
from tests.helpers.complex_test_data_functions import setup_for_get_next_url_for_final_review


@pytest.mark.asyncio
async def test_review_next_source(api_test_helper):
    ath = api_test_helper

    url_mapping = await setup_for_get_next_url_for_final_review(
        db_data_creator=ath.db_data_creator,
        annotation_count=3,
        include_user_annotations=True
    )

    await ath.db_data_creator.agency_auto_suggestions(
        url_id=url_mapping.url_id,
        count=3
    )

    result = await ath.request_validator.review_next_source()

    assert result.url == url_mapping.url
    html_info = result.html_info
    assert html_info.description == "test description"
    assert html_info.title == "test html content"

    annotation_info = result.annotations
    relevant_info = annotation_info.relevant
    assert relevant_info.auto == True
    assert relevant_info.users.relevant == 3
    assert relevant_info.users.not_relevant == 1

    record_type_info = annotation_info.record_type
    assert record_type_info.auto == RecordType.ARREST_RECORDS
    user_d = record_type_info.users
    assert user_d[RecordType.ARREST_RECORDS] == 3
    assert user_d[RecordType.DISPATCH_RECORDINGS] == 2
    assert user_d[RecordType.ACCIDENT_REPORTS] == 1
    assert list(user_d.keys()) == [RecordType.ARREST_RECORDS, RecordType.DISPATCH_RECORDINGS, RecordType.ACCIDENT_REPORTS]


    agency_info = annotation_info.agency
    auto_agency_suggestions = agency_info.auto
    assert auto_agency_suggestions.unknown == False
    assert len(auto_agency_suggestions.suggestions) == 3

    # Check user agency suggestions exist and in descending order of count
    user_agency_suggestions = agency_info.users
    user_agency_suggestions_as_list = list(user_agency_suggestions.values())
    assert len(user_agency_suggestions_as_list) == 3
    for i in range(3):
        assert user_agency_suggestions_as_list[i].count == 3 - i

