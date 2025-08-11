from enum import Enum


class AgencyLookupResponseType(Enum):
    FOUND = "found"
    NOT_FOUND = "not_found"
    ERROR = "error"
