from pydantic import model_validator

from src.collectors.enums import URLStatus
from src.external.url_request.probe.model import URLProbeResponse
from tests.automated.integration.tasks.url.probe.setup.models.planned_response import URLProbePlannedResponse


class TestURLProbeTaskEntry:
    url: str
    url_status: URLStatus
    url_probe_response: URLProbePlannedResponse
