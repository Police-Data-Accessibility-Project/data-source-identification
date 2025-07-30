from typing import final

from typing_extensions import override

from src.core.enums import SuggestionType
from src.core.tasks.url.operators.agency_identification.dtos.suggestion import URLAgencySuggestionInfo
from tests.helpers.data_creator.commands.base import DBDataCreatorCommandBase
from tests.helpers.data_creator.commands.impl.agency import AgencyCommand

@final
class AgencyConfirmedSuggestionCommand(DBDataCreatorCommandBase):

    def __init__(self, url_id: int):
        super().__init__()
        self.url_id = url_id

    @override
    async def run(self) -> int:
        agency_id = await self.run_command(AgencyCommand())
        await self.adb_client.add_confirmed_agency_url_links(
            suggestions=[
                URLAgencySuggestionInfo(
                    url_id=self.url_id,
                    suggestion_type=SuggestionType.CONFIRMED,
                    pdap_agency_id=agency_id
                )
            ]
        )
        return agency_id