from src.db.models.core import UserUrlAgencySuggestion, UserRecordTypeSuggestion, UserRelevantSuggestion

UserSuggestionType = UserUrlAgencySuggestion | UserRelevantSuggestion | UserRecordTypeSuggestion