import datetime
from typing import Optional

from pydantic import BaseModel

class AgenciesSyncResponseInnerInfo(BaseModel):
    display_name: str
    agency_id: int
    state_name: Optional[str]
    county_name: Optional[str]
    locality_name: Optional[str]
    updated_at: datetime.datetime

class AgenciesSyncResponseInfo(BaseModel):
    agencies: list[AgenciesSyncResponseInnerInfo]
