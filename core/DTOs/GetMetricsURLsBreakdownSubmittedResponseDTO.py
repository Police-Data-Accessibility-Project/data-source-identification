from datetime import date

from pydantic import BaseModel

class GetMetricsURLsBreakdownSubmittedInnerDTO(BaseModel):
    week_of: date
    count_submitted: int

class GetMetricsURLsBreakdownSubmittedResponseDTO(BaseModel):
    entries: list