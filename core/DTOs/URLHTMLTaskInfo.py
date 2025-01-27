from dataclasses import dataclass
from typing import Optional

from collector_db.DTOs.URLInfo import URLInfo
from html_tag_collector.DataClassTags import ResponseHTMLInfo
from html_tag_collector.URLRequestInterface import URLResponseInfo


@dataclass
class URLHTMLTaskInfo:
    url_info: URLInfo
    url_response_info: Optional[URLResponseInfo] = None
    html_tag_info: Optional[ResponseHTMLInfo] = None

