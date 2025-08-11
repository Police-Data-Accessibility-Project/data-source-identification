import datetime
from typing import Optional

from pydantic import BaseModel

class AgenciesSyncResponseInnerInfo(BaseModel):
    display_name: str
    agency_id: int
    state_name: str | None
    county_name: str | None
    locality_name: str | None
    updated_at: datetime.datetime

class AgenciesSyncResponseInfo(BaseModel):
    agencies: list[AgenciesSyncResponseInnerInfo]
