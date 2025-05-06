import datetime

from pydantic import BaseModel

class GetMetricsBacklogResponseInnerDTO(BaseModel):
    week_of: datetime.date
    count_pending_total: int

class GetMetricsBacklogResponseDTO(BaseModel):
    entries: list[GetMetricsBacklogResponseInnerDTO]