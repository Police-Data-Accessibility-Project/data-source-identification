from typing import Optional

from pydantic import Field, BaseModel

from src.api.endpoints.annotate.dtos.agency.response import GetNextURLForAgencyAgencyInfo
from src.core.enums import RecordType
from src.core.tasks.operators.url_html.scraper.parser.dtos.response_html import ResponseHTMLInfo


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