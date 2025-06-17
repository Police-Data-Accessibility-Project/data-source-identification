from src.db.models.instantiations.url.suggestion.agency.auto import AutomatedUrlAgencySuggestion
from src.db.models.instantiations.url.suggestion.agency.user import UserUrlAgencySuggestion
from src.db.models.instantiations.url.suggestion.record_type.auto import AutoRecordTypeSuggestion
from src.db.models.instantiations.url.suggestion.record_type.user import UserRecordTypeSuggestion
from src.db.models.instantiations.url.suggestion.relevant.auto import AutoRelevantSuggestion
from src.db.models.instantiations.url.suggestion.relevant.user import UserRelevantSuggestion

PLACEHOLDER_AGENCY_NAME = "PLACEHOLDER_AGENCY_NAME"

STANDARD_ROW_LIMIT = 100

ALL_ANNOTATION_MODELS = [
    AutoRecordTypeSuggestion,
    AutoRelevantSuggestion,
    AutomatedUrlAgencySuggestion,
    UserRelevantSuggestion,
    UserRecordTypeSuggestion,
    UserUrlAgencySuggestion
]

USER_ANNOTATION_MODELS = [
    UserRelevantSuggestion,
    UserRecordTypeSuggestion,
    UserUrlAgencySuggestion
]