from enum import Enum
from typing import Optional

from pydantic import BaseModel

class TaskOperatorOutcome(Enum):
    SUCCESS = "success"
    ERROR = "error"

class TaskOperatorRunInfo(BaseModel):
    task_id: Optional[int]
    linked_url_ids: list[int]
    outcome: TaskOperatorOutcome
    message: str = ""