import datetime
from typing import Optional

from pydantic import BaseModel

from src.collectors.enums import URLStatus


class URLInfo(BaseModel):
    id: int | None = None
    batch_id: int | None= None
    url: str
    collector_metadata: dict | None = None
    outcome: URLStatus = URLStatus.PENDING
    updated_at: datetime.datetime | None = None
    created_at: datetime.datetime | None = None
    name: str | None = None
