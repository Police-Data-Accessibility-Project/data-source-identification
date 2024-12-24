from enum import Enum


class CollectorStatus(Enum):
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    ERRORED = "ERRORED"
    ABORTED = "ABORTED"

class CollectorType(Enum):
    EXAMPLE = "example_collector"
    AUTO_GOOGLER = "auto_googler"

class URLOutcome(Enum):
    PENDING = "pending"
    SUBMITTED = "submitted"
    HUMAN_LABELING = "human_labeling"
    REJECTED = "rejected"
    DUPLICATE = "duplicate"
