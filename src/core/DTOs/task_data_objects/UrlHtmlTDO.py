from typing import Optional

from pydantic import BaseModel

from src.db.DTOs.URLInfo import URLInfo
from src.html_tag_collector.DataClassTags import ResponseHTMLInfo
from src.html_tag_collector.URLRequestInterface import URLResponseInfo


class UrlHtmlTDO(BaseModel):
    url_info: URLInfo
    url_response_info: Optional[URLResponseInfo] = None
    html_tag_info: Optional[ResponseHTMLInfo] = None

