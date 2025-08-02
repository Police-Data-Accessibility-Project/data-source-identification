from pydantic import BaseModel

from src.collectors.enums import URLStatus
from tests.automated.integration.tasks.url.probe.setup.models.planned_response import URLProbePlannedResponse


class TestURLProbeTaskEntry(BaseModel):
    url: str
    url_status: URLStatus
    url_probe_response: URLProbePlannedResponse
    expected_accessed: bool
