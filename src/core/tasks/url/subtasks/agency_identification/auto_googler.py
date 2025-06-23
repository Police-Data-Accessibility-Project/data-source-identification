from typing import Optional

from src.core.enums import SuggestionType
from src.core.tasks.url.operators.agency_identification.dtos.suggestion import URLAgencySuggestionInfo
from src.core.tasks.url.subtasks.agency_identification.base import AgencyIdentificationSubtaskBase


class AutoGooglerAgencyIdentificationSubtask(AgencyIdentificationSubtaskBase):

    async def run(
            self,
            url_id: int,
            collector_metadata: Optional[dict] = None
    ) -> list[URLAgencySuggestionInfo]:
        return [
            URLAgencySuggestionInfo(
                url_id=url_id,
                suggestion_type=SuggestionType.UNKNOWN,
                pdap_agency_id=None,
                agency_name=None,
                state=None,
                county=None,
                locality=None
            )
        ]
