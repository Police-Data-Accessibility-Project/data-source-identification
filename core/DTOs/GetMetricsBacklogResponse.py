from datetime import datetime

from pydantic import BaseModel, field_validator


class GetMetricsBacklogResponseInnerDTO(BaseModel):
    month: str
    count_pending_total: int

    @field_validator("month")
    @classmethod
    def validate_month_format(cls, v: str) -> str:
        try:
            # This will raise ValueError if format doesn't match
            datetime.strptime(v, "%B %Y")
        except ValueError:
            raise ValueError("month must be in the format 'MonthName YYYY' (e.g., 'May 2025')")
        return v

class GetMetricsBacklogResponseDTO(BaseModel):
    entries: list[GetMetricsBacklogResponseInnerDTO]