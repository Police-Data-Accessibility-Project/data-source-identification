from typing import Optional

from core.DTOs.URLAgencySuggestionInfo import URLAgencySuggestionInfo
from core.helpers import process_match_agency_response_to_suggestions
from pdap_api_client.PDAPClient import PDAPClient
from pdap_api_client.DTOs import MatchAgencyResponse


class CKANAgencyIdentificationSubtask:

    def __init__(
            self,
            pdap_client: PDAPClient
    ):
        self.pdap_client = pdap_client

    async def run(
            self,
            url_id: int,
            collector_metadata: Optional[dict]
    ) -> list[URLAgencySuggestionInfo]:
        agency_name = collector_metadata["agency_name"]
        match_agency_response: MatchAgencyResponse = await self.pdap_client.match_agency(
            name=agency_name
        )
        return process_match_agency_response_to_suggestions(
            url_id=url_id,
            match_agency_response=match_agency_response
        )
