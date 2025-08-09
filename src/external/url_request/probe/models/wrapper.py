from pydantic import BaseModel

from src.external.url_request.probe.models.redirect import URLProbeRedirectResponsePair
from src.external.url_request.probe.models.response import URLProbeResponse


class URLProbeResponseOuterWrapper(BaseModel):
    original_url: str
    response: URLProbeResponse | URLProbeRedirectResponsePair

    @property
    def is_redirect(self) -> bool:
        return isinstance(self.response, URLProbeRedirectResponsePair)
