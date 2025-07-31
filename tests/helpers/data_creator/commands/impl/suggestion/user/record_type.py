from random import randint

from src.core.enums import RecordType
from tests.helpers.data_creator.commands.base import DBDataCreatorCommandBase


class UserRecordTypeSuggestionCommand(DBDataCreatorCommandBase):

    def __init__(
        self,
        url_id: int,
        record_type: RecordType,
        user_id: int | None = None,
    ):
        super().__init__()
        self.url_id = url_id
        self.user_id = user_id if user_id is not None else randint(1, 99999999)
        self.record_type = record_type

    async def run(self) -> None:
        await self.adb_client.add_user_record_type_suggestion(
            url_id=self.url_id,
            user_id=self.user_id,
            record_type=self.record_type
        )