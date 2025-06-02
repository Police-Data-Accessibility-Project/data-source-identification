from typing import Optional

from pydantic import Field, BaseModel

from src.api.endpoints.annotate.dtos.agency.response import GetNextURLForAgencyAgencyInfo
from src.api.endpoints.annotate.dtos.shared.base.response import AnnotationInnerResponseInfoBase
from src.core.enums import RecordType


class GetNextURLForAllAnnotationInnerResponse(AnnotationInnerResponseInfoBase):
    agency_suggestions: Optional[list[GetNextURLForAgencyAgencyInfo]] = Field(
        title="The auto-labeler's suggestions for agencies"
    )
    suggested_relevant: Optional[bool] = Field(
        title="Whether the auto-labeler identified the URL as relevant or not"
    )
    suggested_record_type: Optional[RecordType] = Field(
        title="What record type, if any, the auto-labeler identified the URL as"
    )


class GetNextURLForAllAnnotationResponse(BaseModel):
    next_annotation: Optional[GetNextURLForAllAnnotationInnerResponse]