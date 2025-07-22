from src.db.models.instantiations.url.suggestion.agency.auto import AutomatedUrlAgencySuggestion
from src.db.models.instantiations.url.suggestion.agency.user import UserUrlAgencySuggestion
from src.db.models.instantiations.url.suggestion.record_type.auto import AutoRecordTypeSuggestion
from src.db.models.instantiations.url.suggestion.record_type.user import UserRecordTypeSuggestion
from src.db.models.instantiations.url.suggestion.relevant.auto.sqlalchemy import AutoRelevantSuggestion
from src.db.models.instantiations.url.suggestion.relevant.user import UserRelevantSuggestion

UserSuggestionModel = UserRelevantSuggestion or UserRecordTypeSuggestion or UserUrlAgencySuggestion
AutoSuggestionModel = AutoRelevantSuggestion or AutoRecordTypeSuggestion or AutomatedUrlAgencySuggestion
