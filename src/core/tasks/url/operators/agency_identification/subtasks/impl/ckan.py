from typing import final

from typing_extensions import override

from src.core.helpers import process_match_agency_response_to_suggestions
from src.core.tasks.url.operators.agency_identification.dtos.suggestion import URLAgencySuggestionInfo
from src.core.tasks.url.operators.agency_identification.subtasks.impl.base import AgencyIdentificationSubtaskBase
from src.external.pdap.client import PDAPClient
from src.external.pdap.dtos.match_agency.response import MatchAgencyResponse

@final
class CKANAgencyIdentificationSubtask(AgencyIdentificationSubtaskBase):

    def __init__(
            self,
            pdap_client: PDAPClient
    ):
        self.pdap_client = pdap_client

    @override
    async def run(
            self,
            url_id: int,
            collector_metadata: dict | None = None
    ) -> list[URLAgencySuggestionInfo]:
        agency_name = collector_metadata["agency_name"]
        match_agency_response: MatchAgencyResponse = await self.pdap_client.match_agency(
            name=agency_name
        )
        return process_match_agency_response_to_suggestions(
            url_id=url_id,
            match_agency_response=match_agency_response
        )
