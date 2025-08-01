from pydantic import BaseModel

from src.external.url_request.probe.model import URLProbeResponse
from src.db.dtos.url.mapping import URLMapping


class URLProbeTDO(BaseModel):
    url_mapping: URLMapping
    response: URLProbeResponse | None = None
