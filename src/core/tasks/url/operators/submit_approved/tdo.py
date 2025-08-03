from datetime import datetime

from pydantic import BaseModel

from src.core.enums import RecordType


class SubmitApprovedURLTDO(BaseModel):
    url_id: int
    url: str
    record_type: RecordType
    agency_ids: list[int]
    name: str
    description: str | None = None
    approving_user_id: int
    record_formats: list[str] | None = None
    data_portal_type: str | None = None
    supplying_entity: str | None = None
    data_source_id: int | None = None
    request_error: str | None = None

class SubmittedURLInfo(BaseModel):
    url_id: int
    data_source_id: int | None
    request_error: str | None
    submitted_at: datetime | None = None