from src.core.enums import RecordType
from tests.helpers.data_creator.commands.base import DBDataCreatorCommandBase


class AutoRecordTypeSuggestionCommand(DBDataCreatorCommandBase):

    def __init__(
        self,
        url_id: int,
        record_type: RecordType
    ):
        super().__init__()
        self.url_id = url_id
        self.record_type = record_type

    async def run(self) -> None:
        await self.adb_client.add_auto_record_type_suggestion(
            url_id=self.url_id,
            record_type=self.record_type
        )