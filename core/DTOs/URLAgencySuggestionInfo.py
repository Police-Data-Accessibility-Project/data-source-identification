from typing import Optional

from pydantic import BaseModel

from core.enums import SuggestionType


class URLAgencySuggestionInfo(BaseModel):
    url_id: int
    suggestion_type: SuggestionType
    pdap_agency_id: Optional[int] = None
    agency_name: Optional[str] = None
    state: Optional[str] = None
    county: Optional[str] = None
    locality: Optional[str] = None
    user_id: Optional[int] = None
