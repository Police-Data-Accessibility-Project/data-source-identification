from datetime import datetime

from pydantic import BaseModel

class GetMetricsURLsBreakdownSubmittedInnerDTO(BaseModel):
    week_of: datetime.date
    count_submitted: int

class GetMetricsURLsBreakdownSubmittedResponseDTO(BaseModel):
    entries: list