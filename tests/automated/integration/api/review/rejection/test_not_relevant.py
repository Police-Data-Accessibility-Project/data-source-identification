import pytest

from src.api.endpoints.review.enums import RejectionReason
from src.collectors.enums import URLStatus
from tests.automated.integration.api.review.rejection.helpers import run_rejection_test


@pytest.mark.asyncio
async def test_rejection_not_relevant(api_test_helper):
    await run_rejection_test(
        api_test_helper,
        rejection_reason=RejectionReason.NOT_RELEVANT,
        url_status=URLStatus.NOT_RELEVANT
    )
