from src.collectors.enums import URLStatus
from tests.automated.integration.tasks.url.probe.setup.models.entry import TestURLProbeTaskEntry
from tests.automated.integration.tasks.url.probe.setup.models.planned_response import URLProbePlannedResponse

SETUP_ENTRIES: list[TestURLProbeTaskEntry] = [
    TestURLProbeTaskEntry(
        url="https://pending.com",
        url_status=URLStatus.PENDING,
        url_probe_response=URLProbePlannedResponse(
            status_code=200,
            content_type="text/html",
            error=None
        ),
        expected_accessed=True
    ),
    TestURLProbeTaskEntry(
        url="https://submitted.com",
        url_status=URLStatus.SUBMITTED,
        url_probe_response=URLProbePlannedResponse(
            status_code=500,
            content_type=None,
            error="test error"
        ),
        expected_accessed=True
    ),
    TestURLProbeTaskEntry(
        url="https://failure.com",
        url_status=URLStatus.ERROR,
        url_probe_response=URLProbePlannedResponse(
            status_code=None,
            content_type=None,
            error="URL not found"
        ),
        expected_accessed=False
    )
]