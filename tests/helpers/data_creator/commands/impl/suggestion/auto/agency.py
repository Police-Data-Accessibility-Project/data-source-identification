from typing import final

from typing_extensions import override

from src.core.enums import SuggestionType
from src.core.tasks.url.operators.agency_identification.dtos.suggestion import URLAgencySuggestionInfo
from tests.helpers.data_creator.commands.base import DBDataCreatorCommandBase
from tests.helpers.data_creator.commands.impl.agency import AgencyCommand

@final
class AgencyAutoSuggestionsCommand(DBDataCreatorCommandBase):

    def __init__(
        self,
        url_id: int,
        count: int,
        suggestion_type: SuggestionType = SuggestionType.AUTO_SUGGESTION
    ):
        super().__init__()
        if suggestion_type == SuggestionType.UNKNOWN:
            count = 1  # Can only be one auto suggestion if unknown
        self.url_id = url_id
        self.count = count
        self.suggestion_type = suggestion_type

    @override
    async def run(self) -> None:
        suggestions = []
        for _ in range(self.count):
            if self.suggestion_type == SuggestionType.UNKNOWN:
                pdap_agency_id = None
            else:
                pdap_agency_id = await self.run_command(AgencyCommand())
            suggestion = URLAgencySuggestionInfo(
                url_id=self.url_id,
                suggestion_type=self.suggestion_type,
                pdap_agency_id=pdap_agency_id,
                state="Test State",
                county="Test County",
                locality="Test Locality"
            )
            suggestions.append(suggestion)

        await self.adb_client.add_agency_auto_suggestions(
            suggestions=suggestions
        )