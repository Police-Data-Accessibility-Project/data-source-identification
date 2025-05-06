from pydantic import BaseModel

class GetMetricsURLsBreakdownPendingResponseInnerDTO(BaseModel):
    week_created_at: str
    count_pending_total: int
    count_pending_relevant_user: int
    count_pending_record_type_user: int
    count_pending_agency_user: int

class GetMetricsURLsBreakdownPendingResponseDTO(BaseModel):
    entries: list[GetMetricsURLsBreakdownPendingResponseInnerDTO]