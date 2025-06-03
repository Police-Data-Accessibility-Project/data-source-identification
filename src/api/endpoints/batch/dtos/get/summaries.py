import datetime
from typing import Optional

from pydantic import BaseModel

from src.core.enums import BatchStatus


class BatchSummaryURLCounts(BaseModel):
    total: int
    pending: int
    duplicate: int
    not_relevant: int
    submitted: int
    errored: int

class BatchSummary(BaseModel):
    id: int
    strategy: str
    status: BatchStatus
    parameters: dict
    user_id: int
    compute_time: Optional[float]
    date_generated: datetime.datetime
    url_counts: BatchSummaryURLCounts

class GetBatchSummariesResponse(BaseModel):
    results: list[BatchSummary]