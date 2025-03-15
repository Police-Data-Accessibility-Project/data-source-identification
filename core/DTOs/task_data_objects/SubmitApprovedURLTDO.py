from typing import Optional

from pydantic import BaseModel

from core.enums import RecordType


class SubmitApprovedURLTDO(BaseModel):
    url: str
    record_type: RecordType
    agency_id: Optional[int]