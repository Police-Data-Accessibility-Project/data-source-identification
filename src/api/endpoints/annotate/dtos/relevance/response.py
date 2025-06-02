from typing import Optional

from pydantic import BaseModel, Field

from src.api.endpoints.annotate.dtos.shared.base.response import AnnotationInnerResponseInfoBase


class GetNextRelevanceAnnotationResponseInfo(AnnotationInnerResponseInfoBase):
    suggested_relevant: Optional[bool] = Field(
        title="Whether the auto-labeler identified the URL as relevant or not"
    )

class GetNextRelevanceAnnotationResponseOuterInfo(BaseModel):
    next_annotation: Optional[GetNextRelevanceAnnotationResponseInfo]
