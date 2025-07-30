from typing import Optional, __all__, final

from typing_extensions import override

from src.core.enums import SuggestionType
from src.core.tasks.url.operators.agency_identification.dtos.suggestion import URLAgencySuggestionInfo
from src.core.tasks.url.operators.agency_identification.subtasks.base import AgencyIdentificationSubtaskBase

@final
class AutoGooglerAgencyIdentificationSubtask(AgencyIdentificationSubtaskBase):

    @override
    async def run(
            self,
            url_id: int,
            collector_metadata: dict | None = None
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
