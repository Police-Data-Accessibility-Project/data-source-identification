from typing import Optional

from src.source_collectors.muckrock.MuckrockAPIInterface import MuckrockAPIInterface, AgencyLookupResponse, AgencyLookupResponseType
from src.core.DTOs.URLAgencySuggestionInfo import URLAgencySuggestionInfo
from src.core.exceptions import MuckrockAPIError
from src.core.helpers import process_match_agency_response_to_suggestions
from src.pdap_api_client.PDAPClient import PDAPClient
from src.pdap_api_client.DTOs import MatchAgencyResponse


class MuckrockAgencyIdentificationSubtask:

    def __init__(
            self,
            muckrock_api_interface: MuckrockAPIInterface,
            pdap_client: PDAPClient
    ):
        self.muckrock_api_interface = muckrock_api_interface
        self.pdap_client = pdap_client

    async def run(
            self,
            url_id: int,
            collector_metadata: Optional[dict]
    ) -> list[URLAgencySuggestionInfo]:
        muckrock_agency_id = collector_metadata["agency"]
        agency_lookup_response: AgencyLookupResponse = await self.muckrock_api_interface.lookup_agency(
            muckrock_agency_id=muckrock_agency_id
        )
        if agency_lookup_response.type != AgencyLookupResponseType.FOUND:
            raise MuckrockAPIError(
                f"Failed to lookup muckrock agency: {muckrock_agency_id}:"
                f" {agency_lookup_response.type.value}: {agency_lookup_response.error}"
            )

        match_agency_response: MatchAgencyResponse = await self.pdap_client.match_agency(
            name=agency_lookup_response.name
        )
        return process_match_agency_response_to_suggestions(
            url_id=url_id,
            match_agency_response=match_agency_response
        )
