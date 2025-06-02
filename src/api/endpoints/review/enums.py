from enum import Enum


class RejectionReason(Enum):
    NOT_RELEVANT = "NOT_RELEVANT"
    BROKEN_PAGE_404 = "BROKEN_PAGE"
    INDIVIDUAL_RECORD = "INDIVIDUAL_RECORD"
