from pydantic import BaseModel

from collector_db.enums import TaskType


class GetTaskStatusResponseInfo(BaseModel):
    status: TaskType