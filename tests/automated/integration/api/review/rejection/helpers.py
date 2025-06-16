from src.api.endpoints.review.dtos.get import GetNextURLForFinalReviewOuterResponse
from src.api.endpoints.review.dtos.reject import FinalReviewRejectionInfo
from src.api.endpoints.review.enums import RejectionReason
from src.collectors.enums import URLStatus
from src.db.models.instantiations.url.core import URL
from tests.helpers.complex_test_data_functions import setup_for_get_next_url_for_final_review


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
