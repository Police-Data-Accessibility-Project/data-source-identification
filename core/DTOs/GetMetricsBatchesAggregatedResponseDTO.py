from pydantic import BaseModel

from collector_manager.enums import CollectorType


class GetMetricsBatchesAggregatedInnerResponseDTO(BaseModel):
    count_successful_batches: int
    count_failed_batches: int
    count_urls: int
    count_urls_pending: int
    count_urls_submitted: int
    count_urls_rejected: int
    count_urls_errors: int



class GetMetricsBatchesAggregatedResponseDTO(BaseModel):
    total_batches: int
    by_strategy: dict[
        CollectorType,
        GetMetricsBatchesAggregatedInnerResponseDTO
    ]