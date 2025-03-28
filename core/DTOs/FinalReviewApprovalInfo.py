from typing import Optional

from pydantic import BaseModel, Field

from core.enums import RecordType


class FinalReviewApprovalInfo(BaseModel):
    url_id: int = Field(
        title="The id of the URL."
    )
    record_type: Optional[RecordType] = Field(
        title="The final record type of the URL."
              "If none, defers to the existing value from the auto-labeler only if it exists.",
        default=None
    )
    relevant: Optional[bool] = Field(
        title="Final determination on whether the URL is relevant."
              "If none, defers to the existing value from the auto-labeler only if it exists.",
        default=None
    )
    agency_ids: Optional[list[int]] = Field(
        title="The final confirmed agencies for the URL. "
              "If none, defers to an existing confirmed agency only if that exists.",
        default=None
    )
    name: Optional[str] = Field(
        title="The name of the source. "
              "If none, defers to an existing name only if that exists.",
        default=None
    )
    description: Optional[str] = Field(
        title="The description of the source. "
              "If none, defers to an existing description only if that exists.",
        default=None
    )
    record_formats: Optional[list[str]] = Field(
        title="The record formats of the source. "
              "If none, defers to an existing record formats only if that exists.",
        default=None
    )
    data_portal_type: Optional[str] = Field(
        title="The data portal type of the source. "
              "If none, defers to an existing data portal type only if that exists.",
        default=None
    )
    supplying_entity: Optional[str] = Field(
        title="The supplying entity of the source. "
              "If none, defers to an existing supplying entity only if that exists.",
        default=None
    )

