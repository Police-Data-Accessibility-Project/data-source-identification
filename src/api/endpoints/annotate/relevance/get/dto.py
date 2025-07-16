from typing import Optional

from pydantic import BaseModel, Field

from src.api.endpoints.annotate.dtos.shared.base.response import AnnotationInnerResponseInfoBase
from src.core.tasks.url.operators.auto_relevant.models.annotation import RelevanceAnnotationInfo

class RelevanceAnnotationResponseInfo(BaseModel):
    is_relevant: bool | None = Field(
        title="Whether the URL is relevant"
    )
    confidence: float | None = Field(
        title="The confidence of the annotation"
    )
    model_name: str | None = Field(
        title="The name of the model that made the annotation"
    )

class GetNextRelevanceAnnotationResponseInfo(AnnotationInnerResponseInfoBase):
    annotation: RelevanceAnnotationInfo | None = Field(
        title="The auto-labeler's annotation for relevance"
    )

class GetNextRelevanceAnnotationResponseOuterInfo(BaseModel):
    next_annotation: Optional[GetNextRelevanceAnnotationResponseInfo]
