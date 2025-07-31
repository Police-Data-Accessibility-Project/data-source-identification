

from src.core.enums import SuggestionType
from src.core.tasks.url.operators.agency_identification.dtos.suggestion import URLAgencySuggestionInfo

SAMPLE_AGENCY_SUGGESTIONS = [
    URLAgencySuggestionInfo(
        url_id=-1, # This will be overwritten
        suggestion_type=SuggestionType.UNKNOWN,
        pdap_agency_id=None,
        agency_name=None,
        state=None,
        county=None,
        locality=None
    ),
    URLAgencySuggestionInfo(
        url_id=-1, # This will be overwritten
        suggestion_type=SuggestionType.CONFIRMED,
        pdap_agency_id=-1,
        agency_name="Test Agency",
        state="Test State",
        county="Test County",
        locality="Test Locality"
    ),
    URLAgencySuggestionInfo(
        url_id=-1, # This will be overwritten
        suggestion_type=SuggestionType.AUTO_SUGGESTION,
        pdap_agency_id=-1,
        agency_name="Test Agency 2",
        state="Test State 2",
        county="Test County 2",
        locality="Test Locality 2"
    )
]
