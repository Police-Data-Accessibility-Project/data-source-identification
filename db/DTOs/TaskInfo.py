import datetime
from typing import Optional

from pydantic import BaseModel

from db.DTOs.URLErrorInfos import URLErrorPydanticInfo
from db.DTOs.URLInfo import URLInfo
from db.enums import TaskType
from core.enums import BatchStatus


class TaskInfo(BaseModel):
    task_type: TaskType
    task_status: BatchStatus
    updated_at: datetime.datetime
    error_info: Optional[str] = None
    urls: list[URLInfo]
    url_errors: list[URLErrorPydanticInfo]