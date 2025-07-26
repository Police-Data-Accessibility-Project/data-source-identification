from enum import Enum


class MatchAgencyResponseStatus(Enum):
    EXACT_MATCH = "Exact Match"
    PARTIAL_MATCH = "Partial Matches"
    NO_MATCH = "No Match"


class ApprovalStatus(Enum):
    APPROVED = "approved"
    REJECTED = "rejected"
    PENDING = "pending"
    NEEDS_IDENTIFICATION = "needs identification"

class DataSourcesURLStatus(Enum):
    AVAILABLE = "available"
    BROKEN = "broken"
    OK = "ok"
    NONE_FOUND = "none found"