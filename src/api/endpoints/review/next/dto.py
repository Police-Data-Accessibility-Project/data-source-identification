from typing import Optional

from pydantic import BaseModel, Field

from src.api.endpoints.annotate.agency.get.dto import GetNextURLForAgencyAgencyInfo
from src.api.endpoints.annotate.relevance.get.dto import RelevanceAnnotationResponseInfo
from src.core.enums import RecordType, SuggestedStatus
from src.core.tasks.url.operators.html.scraper.parser.dtos.response_html import ResponseHTMLInfo


class FinalReviewAnnotationRelevantInfo(BaseModel):
    auto: RelevanceAnnotationResponseInfo | None = Field(title="Whether the auto-labeler has marked the URL as relevant")
    user: SuggestedStatus | None = Field(
        title="The status marked by a user, if any",
    )

class FinalReviewAnnotationRecordTypeInfo(BaseModel):
    auto: RecordType | None = Field(
        title="The record type suggested by the auto-labeler"
    )
    user: RecordType | None = Field(
        title="The record type suggested by a user",
    )

# region Agency

class FinalReviewAnnotationAgencyAutoInfo(BaseModel):
    unknown: bool = Field(title="Whether the auto-labeler suggested the URL as unknown")
    suggestions: list[GetNextURLForAgencyAgencyInfo] | None = Field(
        title="A list of agencies, if any, suggested by the auto-labeler",
    )

class FinalReviewAnnotationAgencyInfo(BaseModel):
    confirmed: list[GetNextURLForAgencyAgencyInfo] | None = Field(
        title="The confirmed agency for the URL",
    )
    auto: FinalReviewAnnotationAgencyAutoInfo | None = Field(
        title="A single agency or a list of agencies suggested by the auto-labeler",)
    user: GetNextURLForAgencyAgencyInfo | None = Field(
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
    record_formats: list[str] | None = Field(
        title="The record formats of the source",
        default=None
    )
    data_portal_type: str | None = Field(
        title="The data portal type of the source",
        default=None
    )
    supplying_entity: str | None = Field(
        title="The supplying entity of the source",
        default=None
    )

class FinalReviewBatchInfo(BaseModel):
    count_reviewed: int = Field(
        title="The number of URLs in the batch that have been reviewed",
    )
    count_ready_for_review: int = Field(
        title="The number of URLs in the batch that are ready for review",
    )

class GetNextURLForFinalReviewResponse(BaseModel):
    id: int = Field(title="The id of the URL")
    url: str = Field(title="The URL")
    name: str | None = Field(title="The name of the source")
    description: str | None = Field(title="The description of the source")
    html_info: ResponseHTMLInfo = Field(title="The HTML content of the URL")
    annotations: FinalReviewAnnotationInfo = Field(
        title="The annotations for the URL, from both users and the auto-labeler",
    )
    optional_metadata: FinalReviewOptionalMetadata = Field(
        title="Optional metadata for the source",
    )
    batch_info: FinalReviewBatchInfo | None = Field(
        title="Information about the batch",
    )

class GetNextURLForFinalReviewOuterResponse(BaseModel):
    next_source: GetNextURLForFinalReviewResponse | None = Field(
        title="The next source to be reviewed",
    )
    remaining: int = Field(
        title="The number of URLs left to review",
    )