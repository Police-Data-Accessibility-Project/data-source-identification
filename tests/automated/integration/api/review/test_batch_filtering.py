import pytest


@pytest.mark.asyncio
async def test_batch_filtering(
    batch_url_creation_info,
    api_test_helper
):
    ath = api_test_helper
    rv = ath.request_validator

    # Receive null batch info if batch id not provided
    outer_result_no_batch_info = await rv.review_next_source()
    assert outer_result_no_batch_info.next_source.batch_info is None

    # Get batch info if batch id is provided
    outer_result = await ath.request_validator.review_next_source(
        batch_id=batch_url_creation_info.batch_id
    )
    assert outer_result.remaining == 2
    batch_info = outer_result.next_source.batch_info
    assert batch_info.count_reviewed == 4
    assert batch_info.count_ready_for_review == 2

