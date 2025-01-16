from enum import Enum


class BatchStatus(Enum):
    COMPLETE = "complete"
    IN_PROCESS = "in-process"
    ERROR = "error"
    ABORTED = "aborted"

class LabelStudioTaskStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"