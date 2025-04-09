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
    record_formats: Optional[list[str]] = None
    data_portal_type: Optional[str] = None
    supplying_entity: Optional[str] = None
    data_source_id: Optional[int] = None