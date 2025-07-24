import pytest

from src.api.endpoints.review.approve.dto import FinalReviewApprovalInfo
from src.api.endpoints.review.next.dto import GetNextURLForFinalReviewOuterResponse
from src.collectors.enums import URLStatus
from src.core.enums import RecordType
from src.db.constants import PLACEHOLDER_AGENCY_NAME
from src.db.models.instantiations.agency.sqlalchemy import Agency
from src.db.models.instantiations.link.url_agency_.sqlalchemy import LinkURLAgency
from src.db.models.instantiations.url.core.sqlalchemy import URL
from src.db.models.instantiations.url.optional_data_source_metadata import URLOptionalDataSourceMetadata
from tests.helpers.setup.final_review.core import setup_for_get_next_url_for_final_review


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

    assert result.remaining == 0
    assert result.next_source is None

    adb_client = db_data_creator.adb_client
    # Confirm same agency id is listed as confirmed
    urls = await adb_client.get_all(URL)
    assert len(urls) == 1
    url = urls[0]
    assert url.id == url_mapping.url_id
    assert url.record_type == RecordType.ARREST_RECORDS
    assert url.outcome == URLStatus.VALIDATED
    assert url.name == "New Test Name"
    assert url.description == "New Test Description"

    optional_metadata = await adb_client.get_all(URLOptionalDataSourceMetadata)
    assert len(optional_metadata) == 1
    assert optional_metadata[0].data_portal_type == "New Test Data Portal Type"
    assert optional_metadata[0].supplying_entity == "New Test Supplying Entity"
    assert optional_metadata[0].record_formats == ["New Test Record Format", "New Test Record Format 2"]

    # Get agencies
    confirmed_agencies = await adb_client.get_all(LinkURLAgency)
    assert len(confirmed_agencies) == 4
    for agency in confirmed_agencies:
        assert agency.agency_id in agency_ids

    # Check that created agency has placeholder
    agencies = await adb_client.get_all(Agency)
    for agency in agencies:
        if agency.agency_id == additional_agency:
            assert agency.name == PLACEHOLDER_AGENCY_NAME
