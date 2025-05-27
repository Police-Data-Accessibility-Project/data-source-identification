import pytest

from src.db.constants import PLACEHOLDER_AGENCY_NAME
from src.db.models import URL, URLOptionalDataSourceMetadata, ConfirmedURLAgency, Agency
from collector_manager.enums import URLStatus
from src.core.DTOs.FinalReviewApprovalInfo import FinalReviewApprovalInfo, RejectionReason, \
    FinalReviewRejectionInfo
from src.core.DTOs.GetNextURLForFinalReviewResponse import GetNextURLForFinalReviewOuterResponse
from src.core.enums import RecordType, SuggestedStatus
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

@pytest.mark.asyncio
async def test_approve_and_get_next_source_for_review(api_test_helper):
    ath = api_test_helper
    db_data_creator = ath.db_data_creator

    setup_info = await setup_for_get_next_url_for_final_review(
        db_data_creator=db_data_creator,
        include_user_annotations=True
    )
    url_mapping = setup_info.url_mapping

    # Add confirmed agency
    await db_data_creator.confirmed_suggestions([url_mapping.url_id])

    # Additionally, include an agency not yet included in the database
    additional_agency = 999999

    agency_ids = [await db_data_creator.agency() for _ in range(3)]
    agency_ids.append(additional_agency)

    result: GetNextURLForFinalReviewOuterResponse = await ath.request_validator.approve_and_get_next_source_for_review(
        approval_info=FinalReviewApprovalInfo(
            url_id=url_mapping.url_id,
            record_type=RecordType.ARREST_RECORDS,
            agency_ids=agency_ids,
            name="New Test Name",
            description="New Test Description",
            record_formats=["New Test Record Format", "New Test Record Format 2"],
            data_portal_type="New Test Data Portal Type",
            supplying_entity="New Test Supplying Entity"
        )
    )

    assert result.next_source is None

    adb_client = db_data_creator.adb_client
    # Confirm same agency id is listed as confirmed
    urls = await adb_client.get_all(URL)
    assert len(urls) == 1
    url = urls[0]
    assert url.id == url_mapping.url_id
    assert url.record_type == RecordType.ARREST_RECORDS.value
    assert url.outcome == URLStatus.VALIDATED.value
    assert url.name == "New Test Name"
    assert url.description == "New Test Description"

    optional_metadata = await adb_client.get_all(URLOptionalDataSourceMetadata)
    assert len(optional_metadata) == 1
    assert optional_metadata[0].data_portal_type == "New Test Data Portal Type"
    assert optional_metadata[0].supplying_entity == "New Test Supplying Entity"
    assert optional_metadata[0].record_formats == ["New Test Record Format", "New Test Record Format 2"]

    # Get agencies
    confirmed_agencies = await adb_client.get_all(ConfirmedURLAgency)
    assert len(confirmed_agencies) == 4
    for agency in confirmed_agencies:
        assert agency.agency_id in agency_ids

    # Check that created agency has placeholder
    agencies = await adb_client.get_all(Agency)
    for agency in agencies:
        if agency.agency_id == additional_agency:
            assert agency.name == PLACEHOLDER_AGENCY_NAME


async def run_rejection_test(
    api_test_helper,
    rejection_reason: RejectionReason,
    url_status: URLStatus
):
    ath = api_test_helper
    db_data_creator = ath.db_data_creator

    setup_info = await setup_for_get_next_url_for_final_review(
        db_data_creator=db_data_creator,
        annotation_count=3,
        include_user_annotations=True
    )
    url_mapping = setup_info.url_mapping

    result: GetNextURLForFinalReviewOuterResponse = await ath.request_validator.reject_and_get_next_source_for_review(
        review_info=FinalReviewRejectionInfo(
            url_id=url_mapping.url_id,
            rejection_reason=rejection_reason
        )
    )

    assert result.next_source is None

    adb_client = db_data_creator.adb_client
    # Confirm same agency id is listed as rejected
    urls: list[URL] = await adb_client.get_all(URL)
    assert len(urls) == 1
    url = urls[0]
    assert url.id == url_mapping.url_id
    assert url.outcome == url_status.value

@pytest.mark.asyncio
async def test_rejection_not_relevant(api_test_helper):
    await run_rejection_test(
        api_test_helper,
        rejection_reason=RejectionReason.NOT_RELEVANT,
        url_status=URLStatus.NOT_RELEVANT
    )

@pytest.mark.asyncio
async def test_rejection_broken_page(api_test_helper):
    await run_rejection_test(
        api_test_helper,
        rejection_reason=RejectionReason.BROKEN_PAGE_404,
        url_status=URLStatus.NOT_FOUND
    )

@pytest.mark.asyncio
async def test_rejection_individual_record(api_test_helper):
    await run_rejection_test(
        api_test_helper,
        rejection_reason=RejectionReason.INDIVIDUAL_RECORD,
        url_status=URLStatus.INDIVIDUAL_RECORD
    )

