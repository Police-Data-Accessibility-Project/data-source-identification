from typing import Optional

from pydantic import BaseModel

from src.core.tasks.url.operators.url_html.scraper.parser.dtos.response_html import ResponseHTMLInfo
from src.db.models.instantiations.url.core.pydantic import URLInfo
from src.core.tasks.url.operators.url_html.scraper.request_interface.dtos.url_response import URLResponseInfo


class UrlHtmlTDO(BaseModel):
    url_info: URLInfo
    url_response_info: Optional[URLResponseInfo] = None
    html_tag_info: Optional[ResponseHTMLInfo] = None

