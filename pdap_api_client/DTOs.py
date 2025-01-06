from enum import Enum
from http import HTTPStatus
from typing import Optional

from pydantic import BaseModel


class MatchAgencyInfo(BaseModel):
    submitted_name: str
    id: str

class ApprovalStatus(Enum):
    APPROVED = "approved"
    REJECTED = "rejected"
    PENDING = "pending"
    NEEDS_IDENTIFICATION = "needs identification"



class UniqueURLDuplicateInfo(BaseModel):
    original_url: str
    approval_status: ApprovalStatus
    rejection_note: str

class UniqueURLResponseInfo(BaseModel):
    is_unique: bool
    duplicates: list[UniqueURLDuplicateInfo]


class Namespaces(Enum):
    AUTH = "auth"
    MATCH = "match"
    CHECK = "check"


class RequestType(Enum):
    POST = "POST"
    PUT = "PUT"
    GET = "GET"
    DELETE = "DELETE"


class RequestInfo(BaseModel):
    type_: RequestType
    url: str
    json: Optional[dict] = None
    headers: Optional[dict] = None
    params: Optional[dict] = None
    timeout: Optional[int] = 10


class ResponseInfo(BaseModel):
    status_code: HTTPStatus
    data: Optional[dict]
