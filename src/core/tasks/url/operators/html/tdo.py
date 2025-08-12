from typing import Optional

from pydantic import BaseModel

from src.core.tasks.url.operators.html.scraper.parser.dtos.response_html import ResponseHTMLInfo
from src.db.models.impl.url.core.pydantic.info import URLInfo
from src.external.url_request.dtos.url_response import URLResponseInfo


class UrlHtmlTDO(BaseModel):
    url_info: URLInfo
    url_response_info: URLResponseInfo | None = None
    html_tag_info: ResponseHTMLInfo | None = None

