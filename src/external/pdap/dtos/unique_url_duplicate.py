from typing import Optional

from pydantic import BaseModel

from src.external.pdap.enums import ApprovalStatus


class UniqueURLDuplicateInfo(BaseModel):
    original_url: str
    approval_status: ApprovalStatus
    rejection_note: str | None = None
