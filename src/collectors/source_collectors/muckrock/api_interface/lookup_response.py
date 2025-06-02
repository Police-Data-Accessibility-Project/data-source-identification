from typing import Optional

from pydantic import BaseModel

from src.collectors.source_collectors.muckrock.enums import AgencyLookupResponseType


class AgencyLookupResponse(BaseModel):
    name: Optional[str]
    type: AgencyLookupResponseType
    error: Optional[str] = None
