import pytest

from src.api.endpoints.review.enums import RejectionReason
from src.collectors.enums import URLStatus
from tests.automated.integration.api.review.rejection.helpers import run_rejection_test


@pytest.mark.asyncio
async def test_rejection_individual_record(api_test_helper):
    await run_rejection_test(
        api_test_helper,
        rejection_reason=RejectionReason.INDIVIDUAL_RECORD,
        url_status=URLStatus.INDIVIDUAL_RECORD
    )

