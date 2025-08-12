from typing import Optional

from pydantic import Field, BaseModel

from src.api.endpoints.annotate.agency.get.dto import GetNextURLForAgencyAgencyInfo
from src.api.endpoints.annotate.dtos.shared.base.response import AnnotationInnerResponseInfoBase
from src.api.endpoints.annotate.relevance.get.dto import RelevanceAnnotationResponseInfo
from src.core.enums import RecordType


class GetNextURLForAllAnnotationInnerResponse(AnnotationInnerResponseInfoBase):
    agency_suggestions: list[GetNextURLForAgencyAgencyInfo] | None = Field(
        title="The auto-labeler's suggestions for agencies"
    )
    suggested_relevant: RelevanceAnnotationResponseInfo | None = Field(
        title="Whether the auto-labeler identified the URL as relevant or not"
    )
    suggested_record_type: RecordType | None = Field(
        title="What record type, if any, the auto-labeler identified the URL as"
    )


class GetNextURLForAllAnnotationResponse(BaseModel):
    next_annotation: GetNextURLForAllAnnotationInnerResponse | None