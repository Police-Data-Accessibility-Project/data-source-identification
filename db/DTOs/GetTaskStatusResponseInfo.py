from pydantic import BaseModel

from db.enums import TaskType


class GetTaskStatusResponseInfo(BaseModel):
    status: TaskType