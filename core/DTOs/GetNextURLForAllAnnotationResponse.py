from typing import Optional

from pydantic import Field, BaseModel

from core.DTOs.GetNextURLForAgencyAnnotationResponse import GetNextURLForAgencyAgencyInfo
from core.enums import RecordType
from html_tag_collector.DataClassTags import ResponseHTMLInfo


class GetNextURLForAllAnnotationInnerResponse(BaseModel):
    url_id: int
    url: str
    html_info: ResponseHTMLInfo
    agency_suggestions: Optional[list[GetNextURLForAgencyAgencyInfo]]
    suggested_relevant: Optional[bool] = Field(
        title="Whether the auto-labeler identified the URL as relevant or not"
    )
    suggested_record_type: Optional[RecordType] = Field(
        title="What record type, if any, the auto-labeler identified the URL as"
    )


class GetNextURLForAllAnnotationResponse(BaseModel):
    next_annotation: Optional[GetNextURLForAllAnnotationInnerResponse]