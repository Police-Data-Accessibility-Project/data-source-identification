from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from src.core.enums import BatchStatus


class BatchInfo(BaseModel):
    id: Optional[int] = None
    strategy: str
    status: BatchStatus
    parameters: dict
    user_id: int
    total_url_count: Optional[int] = None
    compute_time: Optional[float] = None
    date_generated: Optional[datetime] = None
