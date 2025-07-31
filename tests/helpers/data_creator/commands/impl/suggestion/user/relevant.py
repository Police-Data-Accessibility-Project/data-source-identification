from random import randint
from typing import final

from typing_extensions import override

from src.core.enums import SuggestedStatus
from tests.helpers.data_creator.commands.base import DBDataCreatorCommandBase

@final
class UserRelevantSuggestionCommand(DBDataCreatorCommandBase):

    def __init__(
        self,
        url_id: int,
        user_id: int | None = None,
        suggested_status: SuggestedStatus = SuggestedStatus.RELEVANT
    ):
        super().__init__()
        self.url_id = url_id
        self.user_id = user_id if user_id is not None else randint(1, 99999999)
        self.suggested_status = suggested_status

    @override
    async def run(self) -> None:
        await self.adb_client.add_user_relevant_suggestion(
            url_id=self.url_id,
            user_id=self.user_id,
            suggested_status=self.suggested_status
        )