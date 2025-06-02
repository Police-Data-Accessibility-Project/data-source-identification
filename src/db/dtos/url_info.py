import datetime
from typing import Optional

from pydantic import BaseModel

from src.collectors.enums import URLStatus


class URLInfo(BaseModel):
    id: Optional[int] = None
    batch_id: Optional[int] = None
    url: str
    collector_metadata: Optional[dict] = None
    outcome: URLStatus = URLStatus.PENDING
    updated_at: Optional[datetime.datetime] = None
    created_at: Optional[datetime.datetime] = None
    name: Optional[str] = None
