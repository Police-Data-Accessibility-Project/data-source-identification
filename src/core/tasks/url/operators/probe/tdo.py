from pydantic import BaseModel

from src.db.dtos.url.mapping import URLMapping
from src.external.url_request.probe.models.wrapper import URLProbeResponseOuterWrapper


class URLProbeTDO(BaseModel):
    url_mapping: URLMapping
    response: URLProbeResponseOuterWrapper | None = None
