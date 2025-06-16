from typing import TypeVar

from src.db.models.instantiations.url.suggestion.agency.user import UserUrlAgencySuggestion
from src.db.models.instantiations.url.suggestion.record_type.user import UserRecordTypeSuggestion
from src.db.models.instantiations.url.suggestion.relevant.user import UserRelevantSuggestion
from src.db.queries.base.labels import LabelsBase

UserSuggestionType = UserUrlAgencySuggestion | UserRelevantSuggestion | UserRecordTypeSuggestion

LabelsType = TypeVar("LabelsType", bound=LabelsBase)