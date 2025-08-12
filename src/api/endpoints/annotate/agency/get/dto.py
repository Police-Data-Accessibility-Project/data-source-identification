from typing import Optional

from pydantic import BaseModel

from src.api.endpoints.annotate.dtos.shared.base.response import AnnotationInnerResponseInfoBase
from src.core.enums import SuggestionType

class GetNextURLForAgencyAgencyInfo(BaseModel):
    suggestion_type: SuggestionType
    pdap_agency_id: int | None = None
    agency_name: str | None = None
    state: str | None = None
    county: str | None = None
    locality: str | None = None

class GetNextURLForAgencyAnnotationInnerResponse(AnnotationInnerResponseInfoBase):
    agency_suggestions: list[
        GetNextURLForAgencyAgencyInfo
    ]

class GetNextURLForAgencyAnnotationResponse(BaseModel):
    next_annotation: GetNextURLForAgencyAnnotationInnerResponse | None

