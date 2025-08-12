import datetime
from typing import Optional

from pydantic import BaseModel

from src.db.models.impl.url.core.pydantic.info import URLInfo
from src.db.models.impl.url.error_info.pydantic import URLErrorPydanticInfo
from src.db.enums import TaskType
from src.core.enums import BatchStatus


class TaskInfo(BaseModel):
    task_type: TaskType
    task_status: BatchStatus
    updated_at: datetime.datetime
    error_info: str | None = None
    urls: list[URLInfo]
    url_errors: list[URLErrorPydanticInfo]