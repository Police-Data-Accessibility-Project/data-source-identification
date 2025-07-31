from typing_extensions import override, final

from src.core.enums import SuggestionType
from src.core.tasks.url.operators.agency_identification.dtos.suggestion import URLAgencySuggestionInfo
from src.core.tasks.url.operators.agency_identification.subtasks.impl.base import AgencyIdentificationSubtaskBase

@final
class UnknownAgencyIdentificationSubtask(AgencyIdentificationSubtaskBase):
    """A subtask that returns an unknown suggestion.

    Used in cases where the agency cannot be reliably inferred from the source.
    """

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
