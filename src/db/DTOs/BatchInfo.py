from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from src.core.enums import BatchStatus


class BatchInfo(BaseModel):
    id: Optional[int] = None
    strategy: str
    status: BatchStatus
    parameters: dict
    user_id: int
    total_url_count: int = 0
    original_url_count: int = 0
    duplicate_url_count: int = 0
    strategy_success_rate: Optional[float] = None
    metadata_success_rate: Optional[float] = None
    agency_match_rate: Optional[float] = None
    record_type_match_rate: Optional[float] = None
    record_category_match_rate: Optional[float] = None
    compute_time: Optional[float] = None
    date_generated: Optional[datetime] = None
