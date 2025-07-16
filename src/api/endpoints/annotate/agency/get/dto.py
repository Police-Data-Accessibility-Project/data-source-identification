from typing import Optional

from pydantic import BaseModel

from src.api.endpoints.annotate.dtos.shared.base.response import AnnotationInnerResponseInfoBase
from src.core.enums import SuggestionType

class GetNextURLForAgencyAgencyInfo(BaseModel):
    suggestion_type: SuggestionType
    pdap_agency_id: Optional[int] = None
    agency_name: Optional[str] = None
    state: Optional[str] = None
    county: Optional[str] = None
    locality: Optional[str] = None

class GetNextURLForAgencyAnnotationInnerResponse(AnnotationInnerResponseInfoBase):
    agency_suggestions: list[
        GetNextURLForAgencyAgencyInfo
    ]

class GetNextURLForAgencyAnnotationResponse(BaseModel):
    next_annotation: Optional[GetNextURLForAgencyAnnotationInnerResponse]

