import datetime
from typing import Optional

from pydantic import BaseModel

from src.api.endpoints.batch.dtos.get.summaries.counts import BatchSummaryURLCounts
from src.core.enums import BatchStatus


class BatchSummary(BaseModel):
    id: int
    strategy: str
    status: BatchStatus
    parameters: dict
    user_id: int
    compute_time: float | None
    date_generated: datetime.datetime
    url_counts: BatchSummaryURLCounts
