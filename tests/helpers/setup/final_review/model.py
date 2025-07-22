from typing import Optional

from pydantic import BaseModel

from src.db.dtos.url.mapping import URLMapping


class FinalReviewSetupInfo(BaseModel):
    batch_id: int
    url_mapping: URLMapping
    user_agency_id: Optional[int]
