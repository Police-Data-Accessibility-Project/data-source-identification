import datetime
from typing import Optional

from pydantic import BaseModel


class URLErrorPydanticInfo(BaseModel):
    url_id: int
    error: str
    updated_at: Optional[datetime.datetime] = None