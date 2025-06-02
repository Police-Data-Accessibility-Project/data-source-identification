from typing import Optional

from pydantic import BaseModel

from src.pdap_api.enums import ApprovalStatus


class UniqueURLDuplicateInfo(BaseModel):
    original_url: str
    approval_status: ApprovalStatus
    rejection_note: Optional[str] = None
