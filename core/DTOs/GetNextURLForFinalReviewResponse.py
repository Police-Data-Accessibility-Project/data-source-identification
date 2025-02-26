from typing import Optional

from pydantic import BaseModel, Field

from core.DTOs.GetNextURLForAgencyAnnotationResponse import GetNextURLForAgencyAgencyInfo
from core.enums import RecordType
from html_tag_collector.DataClassTags import ResponseHTMLInfo

# Todo: Add descriptions

class FinalReviewAnnotationRelevantUsersInfo(BaseModel):
    relevant: int = Field(title="Number of users who marked the URL as relevant")
    not_relevant: int = Field(title="Number of users who marked the URL as not relevant")

class FinalReviewAnnotationRelevantInfo(BaseModel):
    auto: Optional[bool] = Field(title="Whether the auto-labeler has marked the URL as relevant")
    users: FinalReviewAnnotationRelevantUsersInfo = Field(
        title="How users identified the relevancy of the source",
    )

class FinalReviewAnnotationRecordTypeInfo(BaseModel):
    auto: Optional[RecordType] = Field(title="The record type suggested by the auto-labeler")
    users: dict[RecordType, int] = Field(
        title="A dictionary, sorted by size and omitting zero values, of all record types suggested by users",
    )

class FinalReviewAnnotationAgencyUserInfo(GetNextURLForAgencyAgencyInfo):
    count: int = Field(title="Number of times suggested by users")

class FinalReviewAnnotationAgencyAutoInfo(BaseModel):
    unknown: bool = Field(title="Whether the auto-labeler suggested the URL as unknown")
    suggestions: Optional[list[GetNextURLForAgencyAgencyInfo]] = Field(
        title="A list of agencies, if any, suggested by the auto-labeler",
    )

class FinalReviewAnnotationAgencyInfo(BaseModel):
    confirmed: Optional[GetNextURLForAgencyAgencyInfo] = Field(
        title="The confirmed agency for the URL",
    )
    auto: Optional[FinalReviewAnnotationAgencyAutoInfo] = Field(
        title="A single agency or a list of agencies suggested by the auto-labeler",)
    users: Optional[dict[int, FinalReviewAnnotationAgencyUserInfo]] = Field(
        title="A list, sorted by size, of all agencies suggested by users",
    )

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

class GetNextURLForFinalReviewResponse(BaseModel):
    id: int = Field(title="The id of the URL")
    url: str = Field(title="The URL")
    html_info: ResponseHTMLInfo = Field(title="The HTML content of the URL")
    annotations: FinalReviewAnnotationInfo = Field(
        title="The annotations for the URL, from both users and the auto-labeler",
    )

class GetNextURLForFinalReviewOuterResponse(BaseModel):
    next_source: Optional[GetNextURLForFinalReviewResponse] = Field(
        title="The next source to be reviewed",
    )