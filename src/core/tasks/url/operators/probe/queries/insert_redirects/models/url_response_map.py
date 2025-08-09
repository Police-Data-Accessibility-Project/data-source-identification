from pydantic import BaseModel

from src.db.dtos.url.mapping import URLMapping
from src.external.url_request.probe.models.response import URLProbeResponse


class URLResponseMapping(BaseModel):
    url_mapping: URLMapping
    response: URLProbeResponse