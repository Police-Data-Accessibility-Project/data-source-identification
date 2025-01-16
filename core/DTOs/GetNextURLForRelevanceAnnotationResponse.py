from typing import Optional

from pydantic import BaseModel

from core.DTOs.RelevanceAnnotationRequestInfo import RelevanceAnnotationRequestInfo


class GetNextURLForRelevanceAnnotationResponse(BaseModel):
    next_annotation: Optional[RelevanceAnnotationRequestInfo] = None
