from typing import Optional

from pydantic import BaseModel

from src.collectors.impl.muckrock.enums import AgencyLookupResponseType


class AgencyLookupResponse(BaseModel):
    name: Optional[str]
    type: AgencyLookupResponseType
    error: Optional[str] = None
