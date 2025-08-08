from pydantic import BaseModel

from src.collectors.enums import URLStatus
from src.external.url_request.probe.models.wrapper import URLProbeResponseOuterWrapper
from tests.automated.integration.tasks.url.probe.setup.models.planned_response import URLProbePlannedResponse


class TestURLProbeTaskEntry(BaseModel):
    url: str
    url_status: URLStatus
    planned_response: URLProbeResponseOuterWrapper