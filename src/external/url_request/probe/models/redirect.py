from pydantic import BaseModel

from src.external.url_request.probe.models.response import URLProbeResponse


class URLProbeRedirectResponsePair(BaseModel):
    source: URLProbeResponse
    destination: URLProbeResponse