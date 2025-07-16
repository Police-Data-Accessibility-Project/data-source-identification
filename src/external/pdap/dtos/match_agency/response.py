from typing import List

from pydantic import BaseModel

from src.external.pdap.dtos.match_agency.post import MatchAgencyInfo
from src.external.pdap.enums import MatchAgencyResponseStatus


class MatchAgencyResponse(BaseModel):
    status: MatchAgencyResponseStatus
    matches: List[MatchAgencyInfo]
