from pydantic import BaseModel

from src.db.enums import TaskType


class GetTaskStatusResponseInfo(BaseModel):
    status: TaskType