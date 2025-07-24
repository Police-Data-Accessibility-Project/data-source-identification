from enum import Enum


class SyncResponseOrder(Enum):
    """Represents which sync response the entry is in."""
    FIRST = 1
    SECOND = 2
    # No entries should be in 3
    THIRD = 3


class AgencyAssigned(Enum):
    """Represents which of several pre-created agencies the entry is assigned to."""
    ONE = 1
    TWO = 2
    THREE = 3
