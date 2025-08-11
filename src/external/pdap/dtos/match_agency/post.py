from typing import Optional

from pydantic import BaseModel


class MatchAgencyInfo(BaseModel):
    id: int
    submitted_name: str
    state: str | None = None
    county: str | None = None
    locality: str | None = None
