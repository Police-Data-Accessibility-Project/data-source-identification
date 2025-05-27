from typing import Optional

from src.core.DTOs.URLAgencySuggestionInfo import URLAgencySuggestionInfo
from src.core.classes.subtasks.AgencyIdentificationSubtaskBase import AgencyIdentificationSubtaskBase
from src.core.enums import SuggestionType


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
