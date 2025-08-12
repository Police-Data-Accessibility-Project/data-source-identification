from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class LogInfo(BaseModel):
    id: int | None = None
    log: str
    batch_id: int
    created_at: datetime | None = None
