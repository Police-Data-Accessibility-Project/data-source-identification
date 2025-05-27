from datetime import datetime

from pydantic import BaseModel

from src.collector_manager.enums import CollectorType
from src.core.enums import BatchStatus


class GetMetricsBatchesBreakdownInnerResponseDTO(BaseModel):
    batch_id: int
    strategy: CollectorType
    status: BatchStatus
    created_at: datetime
    count_url_total: int
    count_url_pending: int
    count_url_submitted: int
    count_url_rejected: int
    count_url_error: int
    count_url_validated: int

class GetMetricsBatchesBreakdownResponseDTO(BaseModel):
    batches: list[GetMetricsBatchesBreakdownInnerResponseDTO]