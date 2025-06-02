from src.core.tasks.operators.agency_identification.dtos.suggestion import URLAgencySuggestionInfo
from src.core.enums import SuggestionType
from src.core.exceptions import MatchAgencyError
from src.pdap_api.dtos.match_agency.response import MatchAgencyResponse
from src.pdap_api.enums import MatchAgencyResponseStatus


def process_match_agency_response_to_suggestions(
    url_id: int,
    match_agency_response: MatchAgencyResponse
) -> list[URLAgencySuggestionInfo]:
    if match_agency_response.status == MatchAgencyResponseStatus.EXACT_MATCH:
        match = match_agency_response.matches[0]
        return [
            URLAgencySuggestionInfo(
                url_id=url_id,
                suggestion_type=SuggestionType.CONFIRMED,
                pdap_agency_id=int(match.id),
                agency_name=match.submitted_name,
                state=match.state,
                county=match.county,
            )
        ]
    if match_agency_response.status == MatchAgencyResponseStatus.NO_MATCH:
        return [
            URLAgencySuggestionInfo(
                url_id=url_id,
                suggestion_type=SuggestionType.UNKNOWN,
            )
        ]

    if match_agency_response.status != MatchAgencyResponseStatus.PARTIAL_MATCH:
        raise MatchAgencyError(
            f"Unknown Match Agency Response Status: {match_agency_response.status}"
        )

    return [
        URLAgencySuggestionInfo(
            url_id=url_id,
            suggestion_type=SuggestionType.AUTO_SUGGESTION,
            pdap_agency_id=match.id,
            agency_name=match.submitted_name,
            state=match.state,
            county=match.county,
            locality=match.locality
        )
        for match in match_agency_response.matches
    ]
