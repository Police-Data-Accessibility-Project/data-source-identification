from typing import Optional

from pydantic import BaseModel, Field

from collector_db.DTOs.URLMapping import URLMapping
from core.DTOs.ResponseURLInfo import ResponseURLInfo
from html_tag_collector.DataClassTags import ResponseHTMLInfo


class GetNextRelevanceAnnotationResponseInfo(BaseModel):
    url_info: URLMapping = Field(
        title="Information about the URL"
    )
    suggested_relevant: Optional[bool] = Field(
        title="Whether the auto-labeler identified the URL as relevant or not"
    )
    html_info: ResponseHTMLInfo = Field(
        title="HTML information about the URL"
    )

class GetNextRelevanceAnnotationResponseOuterInfo(BaseModel):
    next_annotation: Optional[GetNextRelevanceAnnotationResponseInfo]
