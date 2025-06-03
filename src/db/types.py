from typing import TypeVar

from src.db.models.core import UserUrlAgencySuggestion, UserRecordTypeSuggestion, UserRelevantSuggestion
from src.db.queries.base.labels import LabelsBase

UserSuggestionType = UserUrlAgencySuggestion | UserRelevantSuggestion | UserRecordTypeSuggestion

LabelsType = TypeVar("LabelsType", bound=LabelsBase)