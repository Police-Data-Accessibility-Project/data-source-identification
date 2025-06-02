from typing import Optional

from pydantic import BaseModel

from src.core.tasks.enums import TaskOperatorOutcome


class TaskOperatorRunInfo(BaseModel):
    task_id: Optional[int]
    linked_url_ids: list[int]
    outcome: TaskOperatorOutcome
    message: str = ""