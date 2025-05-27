import datetime

from pydantic import BaseModel

from db.enums import TaskType
from core.enums import BatchStatus


class GetTasksResponseTaskInfo(BaseModel):
    task_id: int
    type: TaskType
    status: BatchStatus
    url_count: int
    url_error_count: int
    updated_at: datetime.datetime


class GetTasksResponse(BaseModel):
    tasks: list[GetTasksResponseTaskInfo]
