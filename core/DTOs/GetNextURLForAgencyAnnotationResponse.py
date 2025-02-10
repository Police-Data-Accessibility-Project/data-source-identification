from typing import Optional, Literal

from pydantic import BaseModel

from core.enums import SuggestionType
from html_tag_collector.DataClassTags import ResponseHTMLInfo

class GetNextURLForAgencyAgencyInfo(BaseModel):
    suggestion_type: SuggestionType
    pdap_agency_id: Optional[int] = None
    agency_name: Optional[str] = None
    state: Optional[str] = None
    county: Optional[str] = None
    locality: Optional[str] = None

class GetNextURLForAgencyAnnotationInnerResponse(BaseModel):
    url_id: int
    url: str
    agency_suggestions: list[
        GetNextURLForAgencyAgencyInfo
    ]
    html_info: ResponseHTMLInfo

class GetNextURLForAgencyAnnotationResponse(BaseModel):
    next_annotation: Optional[GetNextURLForAgencyAnnotationInnerResponse]

class URLAgencyAnnotationPostInfo(BaseModel):
    is_new: bool = False
    suggested_agency: Optional[int] = None