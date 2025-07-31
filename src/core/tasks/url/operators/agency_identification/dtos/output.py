from pydantic import BaseModel

from src.core.tasks.url.operators.agency_identification.dtos.suggestion import URLAgencySuggestionInfo
from src.db.models.instantiations.url.error_info.pydantic import URLErrorPydanticInfo


class GetAgencySuggestionsOutput(BaseModel):
    error_infos: list[URLErrorPydanticInfo]
    agency_suggestions: list[URLAgencySuggestionInfo]