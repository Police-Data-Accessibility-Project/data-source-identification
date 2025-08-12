from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from src.core.enums import BatchStatus


class BatchInfo(BaseModel):
    id: int | None = None
    strategy: str
    status: BatchStatus
    parameters: dict
    user_id: int
    total_url_count: int | None = None
    compute_time: float | None = None
    date_generated: datetime | None = None
