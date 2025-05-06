from pydantic import BaseModel

class GetMetricsURLsBreakdownPendingResponseInnerDTO(BaseModel):
    week_created_at: str
    count_pending_total: int
    count_pending_relevant: int
    count_pending_record_type: int
    count_pending_agency: int
    count_pending_final: int

class GetMetricsURLsBreakdownPendingResponseDTO(BaseModel):
    entries: list[GetMetricsURLsBreakdownPendingResponseInnerDTO]