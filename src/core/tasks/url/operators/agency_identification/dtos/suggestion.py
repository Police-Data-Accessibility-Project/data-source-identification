from typing import Optional

from pydantic import BaseModel

from src.core.enums import SuggestionType


class URLAgencySuggestionInfo(BaseModel):
    url_id: int
    suggestion_type: SuggestionType = SuggestionType.UNKNOWN
    pdap_agency_id: int | None = None
    agency_name: str | None = None
    state: str | None = None
    county: str | None = None
    locality: str | None = None
    user_id: int | None = None
