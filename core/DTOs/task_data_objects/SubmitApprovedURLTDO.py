from typing import Optional

from pydantic import BaseModel

from core.enums import RecordType


class SubmitApprovedURLTDO(BaseModel):
    url_id: int
    url: str
    record_type: RecordType
    agency_ids: list[int]
    name: str
    description: str
    approving_user_id: int
    record_formats: Optional[list[str]] = None
    data_portal_type: Optional[str] = None
    supplying_entity: Optional[str] = None
    data_source_id: Optional[int] = None
    request_error: Optional[str] = None

class SubmittedURLInfo(BaseModel):
    url_id: int
    data_source_id: Optional[int]
    request_error: Optional[str]