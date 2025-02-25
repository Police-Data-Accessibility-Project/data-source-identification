from typing import Optional

from pydantic import BaseModel, Field

from core.enums import RecordType


class FinalReviewApprovalInfo(BaseModel):
    url_id: int = Field(
        title="The id of the URL."
    )
    record_type: RecordType = Field(
        title="The final record type of the URL."
              "If none, defers to the existing value from the auto-labeler only if it exists.",
        default=None
    )
    relevant: bool = Field(
        title="Final determination on whether the URL is relevant."
              "If none, defers to the existing value from the auto-labeler only if it exists.",
        default=None
    )
    agency_id: Optional[int] = Field(
        title="The final confirmed agency for the URL. "
              "If none, defers to an existing confirmed agency only if that exists.",
        default=None
    )
