from pydantic import BaseModel, field_validator
from datetime import datetime

class GetMetricsURLsBreakdownPendingResponseInnerDTO(BaseModel):
    month: str
    count_pending_total: int
    count_pending_relevant_user: int
    count_pending_record_type_user: int
    count_pending_agency_user: int

    @field_validator("month")
    @classmethod
    def validate_month_format(cls, v: str) -> str:
        try:
            # This will raise ValueError if format doesn't match
            datetime.strptime(v, "%B %Y")
        except ValueError:
            raise ValueError("month must be in the format 'MonthName YYYY' (e.g., 'May 2025')")
        return v

class GetMetricsURLsBreakdownPendingResponseDTO(BaseModel):
    entries: list[GetMetricsURLsBreakdownPendingResponseInnerDTO]