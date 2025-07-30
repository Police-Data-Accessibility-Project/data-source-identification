from typing import Optional, final

from typing_extensions import override

from src.collectors.source_collectors.muckrock.api_interface.core import MuckrockAPIInterface
from src.collectors.source_collectors.muckrock.api_interface.lookup_response import AgencyLookupResponse
from src.collectors.source_collectors.muckrock.enums import AgencyLookupResponseType
from src.core.exceptions import MuckrockAPIError
from src.core.helpers import process_match_agency_response_to_suggestions
from src.core.tasks.url.operators.agency_identification.dtos.suggestion import URLAgencySuggestionInfo
from src.core.tasks.url.operators.agency_identification.subtasks.base import AgencyIdentificationSubtaskBase
from src.external.pdap.client import PDAPClient
from src.external.pdap.dtos.match_agency.response import MatchAgencyResponse

@final
class MuckrockAgencyIdentificationSubtask(AgencyIdentificationSubtaskBase):

    def __init__(
            self,
            muckrock_api_interface: MuckrockAPIInterface,
            pdap_client: PDAPClient
    ):
        self.muckrock_api_interface = muckrock_api_interface
        self.pdap_client = pdap_client

    @override
    async def run(
            self,
            url_id: int,
            collector_metadata: dict | None = None
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
