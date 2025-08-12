from typing import Optional

from pydantic import BaseModel

from src.core.tasks.url.enums import TaskOperatorOutcome
from src.db.enums import TaskType


class TaskOperatorRunInfo(BaseModel):
    task_id: int | None
    task_type: TaskType
    outcome: TaskOperatorOutcome
    message: str = ""