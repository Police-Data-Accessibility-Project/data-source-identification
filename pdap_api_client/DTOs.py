from enum import Enum
from http import HTTPStatus
from typing import Optional, List

from pydantic import BaseModel

from pdap_api_client.enums import MatchAgencyResponseStatus


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
    rejection_note: str

class UniqueURLResponseInfo(BaseModel):
    is_unique: bool
    duplicates: list[UniqueURLDuplicateInfo]


class Namespaces(Enum):
    AUTH = "auth"
    MATCH = "match"
    CHECK = "check"
    DATA_SOURCES = "data-sources"
    SOURCE_COLLECTOR = "source-collector"


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

    def kwargs(self) -> dict:
        d = {
            "url": self.url,
        }
        if self.json is not None:
            d['json'] = self.json
        if self.headers is not None:
            d['headers'] = self.headers
        return d


class ResponseInfo(BaseModel):
    status_code: HTTPStatus
    data: Optional[dict]


class MatchAgencyResponse(BaseModel):
    status: MatchAgencyResponseStatus
    matches: List[MatchAgencyInfo]
