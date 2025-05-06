import datetime

from pydantic import BaseModel

from collector_manager.enums import CollectorType


class GetMetricsBatchesBreakdownInnerResponseDTO(BaseModel):
    batch_id: str
    strategy: CollectorType
    created_at: datetime.datetime
    count_url_total: int
    count_url_pending: int
    count_url_submitted: int
    count_url_rejected: int
    count_url_error: int

class GetMetricsBatchesBreakdownResponseDTO(BaseModel):
    batches: list[GetMetricsBatchesBreakdownInnerResponseDTO]