from typing import Optional

from pydantic import BaseModel

from core.DTOs.AnnotationRequestInfo import AnnotationRequestInfo


class GetNextURLForAnnotationResponse(BaseModel):
    next_annotation: Optional[AnnotationRequestInfo] = None
