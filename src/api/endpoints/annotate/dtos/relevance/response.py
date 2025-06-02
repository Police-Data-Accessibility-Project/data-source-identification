from typing import Optional

from pydantic import BaseModel, Field

from src.db.dtos.url_mapping import URLMapping
from src.core.tasks.operators.url_html.scraper.parser.dtos.response_html import ResponseHTMLInfo


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
