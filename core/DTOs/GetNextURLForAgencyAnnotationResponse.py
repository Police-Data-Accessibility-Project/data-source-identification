from typing import Optional, Literal

from core.enums import SuggestionType
from html_tag_collector.DataClassTags import ResponseHTMLInfo

class GetNextURLForAgencyAgencyInfo:
    suggestion_type: SuggestionType
    pdap_agency_id: Optional[int] = None
    agency_name: Optional[str] = None
    state: Optional[str] = None
    county: Optional[str] = None
    locality: Optional[str] = None

class GetNextURLForAgencyAnnotationResponse:
    url_id: int
    agency_suggestions: list[
        GetNextURLForAgencyAgencyInfo
    ]
    html_info: ResponseHTMLInfo

class URLAgencyAnnotationPostInfo:
    suggested_agency: int | Literal["NEW"]