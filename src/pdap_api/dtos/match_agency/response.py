from typing import List

from pydantic import BaseModel

from src.pdap_api.dtos.match_agency.post import MatchAgencyInfo
from src.pdap_api.enums import MatchAgencyResponseStatus


class MatchAgencyResponse(BaseModel):
    status: MatchAgencyResponseStatus
    matches: List[MatchAgencyInfo]
