from enum import Enum
from typing import Optional, List

from pydantic import BaseModel

from src.pdap_api_client.enums import MatchAgencyResponseStatus


class MatchAgencyInfo(BaseModel):
    id: int
    submitted_name: str
    state: Optional[str] = None
    county: Optional[str] = None
    locality: Optional[str] = None

class ApprovalStatus(Enum):
    APPROVED = "approved"
    REJECTED = "rejected"
    PENDING = "pending"
    NEEDS_IDENTIFICATION = "needs identification"

class UniqueURLDuplicateInfo(BaseModel):
    original_url: str
    approval_status: ApprovalStatus
    rejection_note: Optional[str] = None

class MatchAgencyResponse(BaseModel):
    status: MatchAgencyResponseStatus
    matches: List[MatchAgencyInfo]
