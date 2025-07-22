import pytest

from src.api.endpoints.review.approve.dto import FinalReviewApprovalInfo
from src.collectors.enums import URLStatus
from src.core.enums import RecordType
from src.db.models.instantiations.confirmed_url_agency import ConfirmedURLAgency
from src.db.models.instantiations.url.core.sqlalchemy import URL
from src.db.models.instantiations.url.optional_data_source_metadata import URLOptionalDataSourceMetadata
from src.db.models.instantiations.url.reviewing_user import ReviewingUserURL
from tests.helpers.setup.final_review.core import setup_for_get_next_url_for_final_review
from tests.helpers.db_data_creator import DBDataCreator


@pytest.mark.asyncio
async def test_approve_url_basic(db_data_creator: DBDataCreator):
    setup_info = await setup_for_get_next_url_for_final_review(
        db_data_creator=db_data_creator,
        annotation_count=3,
        include_user_annotations=True
    )
    url_mapping = setup_info.url_mapping

    # Add confirmed agency
    agency_id = await db_data_creator.agency_confirmed_suggestion(
        url_id=url_mapping.url_id
    )

    adb_client = db_data_creator.adb_client
    # Approve URL. Only URL should be affected. No other properties should be changed.
    await adb_client.approve_url(
        approval_info=FinalReviewApprovalInfo(
            url_id=url_mapping.url_id,
            record_type=RecordType.ARREST_RECORDS,
            relevant=True,
        ),
        user_id=1
    )

    # Confirm same agency id is listed as confirmed
    urls: list[URL] = await adb_client.get_all(URL)
    assert len(urls) == 1
    url = urls[0]
    assert url.id == url_mapping.url_id
    assert url.record_type == RecordType.ARREST_RECORDS.value
    assert url.outcome == URLStatus.VALIDATED.value
    assert url.name == "Test Name"
    assert url.description == "Test Description"

    confirmed_agency: list[ConfirmedURLAgency] = await adb_client.get_all(ConfirmedURLAgency)
    assert len(confirmed_agency) == 1
    assert confirmed_agency[0].url_id == url_mapping.url_id
    assert confirmed_agency[0].agency_id == agency_id

    approving_user_urls: list[ReviewingUserURL] = await adb_client.get_all(ReviewingUserURL)
    assert len(approving_user_urls) == 1
    assert approving_user_urls[0].user_id == 1
    assert approving_user_urls[0].url_id == url_mapping.url_id

    optional_metadata: list[URLOptionalDataSourceMetadata] = await adb_client.get_all(URLOptionalDataSourceMetadata)
    assert len(optional_metadata) == 1
    assert optional_metadata[0].url_id == url_mapping.url_id
    assert optional_metadata[0].record_formats == ["Test Record Format", "Test Record Format 2"]
    assert optional_metadata[0].data_portal_type == "Test Data Portal Type"
    assert optional_metadata[0].supplying_entity == "Test Supplying Entity"
