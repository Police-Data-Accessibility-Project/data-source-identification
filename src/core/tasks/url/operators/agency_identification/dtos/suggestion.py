from typing import Optional

from pydantic import BaseModel

from src.core.enums import SuggestionType


class URLAgencySuggestionInfo(BaseModel):
    url_id: int
    suggestion_type: SuggestionType = SuggestionType.UNKNOWN
    pdap_agency_id: Optional[int] = None
    agency_name: Optional[str] = None
    state: Optional[str] = None
    county: Optional[str] = None
    locality: Optional[str] = None
    user_id: Optional[int] = None
