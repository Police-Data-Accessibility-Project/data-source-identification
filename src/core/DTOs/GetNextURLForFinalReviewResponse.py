from typing import Optional

from pydantic import BaseModel, Field

from src.core.DTOs.GetNextURLForAgencyAnnotationResponse import GetNextURLForAgencyAgencyInfo
from src.core.enums import RecordType, SuggestedStatus
from src.html_tag_collector.DataClassTags import ResponseHTMLInfo

class FinalReviewAnnotationRelevantInfo(BaseModel):
    auto: Optional[bool] = Field(title="Whether the auto-labeler has marked the URL as relevant")
    user: Optional[SuggestedStatus] = Field(
        title="The status marked by a user, if any",
    )

class FinalReviewAnnotationRecordTypeInfo(BaseModel):
    auto: Optional[RecordType] = Field(
        title="The record type suggested by the auto-labeler"
    )
    user: Optional[RecordType] = Field(
        title="The record type suggested by a user",
    )

# region Agency

class FinalReviewAnnotationAgencyAutoInfo(BaseModel):
    unknown: bool = Field(title="Whether the auto-labeler suggested the URL as unknown")
    suggestions: Optional[list[GetNextURLForAgencyAgencyInfo]] = Field(
        title="A list of agencies, if any, suggested by the auto-labeler",
    )

class FinalReviewAnnotationAgencyInfo(BaseModel):
    confirmed: Optional[list[GetNextURLForAgencyAgencyInfo]] = Field(
        title="The confirmed agency for the URL",
    )
    auto: Optional[FinalReviewAnnotationAgencyAutoInfo] = Field(
        title="A single agency or a list of agencies suggested by the auto-labeler",)
    user: Optional[GetNextURLForAgencyAgencyInfo] = Field(
        title="A single agency suggested by a user",
    )
# endregion

class FinalReviewAnnotationInfo(BaseModel):
    relevant: FinalReviewAnnotationRelevantInfo = Field(
        title="User and auto annotations for relevancy",
    )
    record_type: FinalReviewAnnotationRecordTypeInfo = Field(
        title="User and auto annotations for record type",
    )
    agency: FinalReviewAnnotationAgencyInfo = Field(
        title="User and auto annotations for agency",
    )

class FinalReviewOptionalMetadata(BaseModel):
    record_formats: Optional[list[str]] = Field(
        title="The record formats of the source",
        default=None
    )
    data_portal_type: Optional[str] = Field(
        title="The data portal type of the source",
        default=None
    )
    supplying_entity: Optional[str] = Field(
        title="The supplying entity of the source",
        default=None
    )

class GetNextURLForFinalReviewResponse(BaseModel):
    id: int = Field(title="The id of the URL")
    url: str = Field(title="The URL")
    name: Optional[str] = Field(title="The name of the source")
    description: Optional[str] = Field(title="The description of the source")
    html_info: ResponseHTMLInfo = Field(title="The HTML content of the URL")
    annotations: FinalReviewAnnotationInfo = Field(
        title="The annotations for the URL, from both users and the auto-labeler",
    )
    optional_metadata: FinalReviewOptionalMetadata = Field(
        title="Optional metadata for the source",
    )

class GetNextURLForFinalReviewOuterResponse(BaseModel):
    next_source: Optional[GetNextURLForFinalReviewResponse] = Field(
        title="The next source to be reviewed",
    )