from enum import Enum


class MatchAgencyResponseStatus(Enum):
    EXACT_MATCH = "Exact Match"
    PARTIAL_MATCH = "Partial Matches"
    NO_MATCH = "No Match"
