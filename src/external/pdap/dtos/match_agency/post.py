from typing import Optional

from pydantic import BaseModel


class MatchAgencyInfo(BaseModel):
    id: int
    submitted_name: str
    state: Optional[str] = None
    county: Optional[str] = None
    locality: Optional[str] = None
