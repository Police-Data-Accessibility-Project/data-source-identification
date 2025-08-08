from src.external.url_request.probe.models.response import URLProbeResponse
from tests.automated.integration.tasks.url.probe.setup.data import SETUP_ENTRIES
from tests.automated.integration.tasks.url.probe.setup.models.entry import TestURLProbeTaskEntry


def build_url_to_probe_response_map(
) -> dict[str, URLProbeResponse]:
    d = {}
    for entry in SETUP_ENTRIES:
        probe_response = URLProbeResponse(
            url=entry.url,
            status_code=entry.url_probe_response.status_code,
            content_type=entry.url_probe_response.content_type,
            error=entry.url_probe_response.error
        )
        d[entry.url] = probe_response
    return d

def build_url_to_entry_map(
) -> dict[str, TestURLProbeTaskEntry]:
    d = {}
    for entry in SETUP_ENTRIES:
        d[entry.url] = entry
    return d