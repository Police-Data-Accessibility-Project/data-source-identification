from pydantic import BaseModel

from src.collectors.enums import URLStatus
from src.external.url_request.probe.models.wrapper import URLProbeResponseOuterWrapper


class TestURLProbeTaskEntry(BaseModel):
    url: str
    url_status: URLStatus
    planned_response: URLProbeResponseOuterWrapper