import datetime
from typing import Optional

from pydantic import BaseModel


class URLErrorPydanticInfo(BaseModel):
    task_id: int
    url_id: int
    error: str
    updated_at: Optional[datetime.datetime] = None