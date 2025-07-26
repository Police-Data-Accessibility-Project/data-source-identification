import datetime
from typing import Optional

from pydantic import BaseModel

from src.db.models.instantiations.url.error_info.pydantic import URLErrorPydanticInfo
from src.db.models.instantiations.url.core.pydantic import URLInfo
from src.db.enums import TaskType
from src.core.enums import BatchStatus


class TaskInfo(BaseModel):
    task_type: TaskType
    task_status: BatchStatus
    updated_at: datetime.datetime
    error_info: Optional[str] = None
    urls: list[URLInfo]
    url_errors: list[URLErrorPydanticInfo]