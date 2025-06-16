from pydantic import BaseModel


class GetMetricsURLsAggregatedPendingResponseDTO(BaseModel):
    all: int
    relevant: int
    record_type: int
    agency: int
    annotations_0: int
    annotations_1: int
    annotations_2: int
    annotations_3: int