from src.core.enums import BatchStatus
from tests.helpers.batch_creation_parameters.core import TestBatchCreationParameters
from tests.helpers.data_creator.commands.base import DBDataCreatorCommandBase
from tests.helpers.data_creator.commands.impl.batch import DBDataCreatorBatchCommand
from tests.helpers.data_creator.commands.impl.urls_v2.core import URLsV2Command
from tests.helpers.data_creator.models.creation_info.batch.v2 import BatchURLCreationInfoV2


class BatchV2Command(DBDataCreatorCommandBase):

    def __init__(
        self,
        parameters: TestBatchCreationParameters
    ):
        super().__init__()
        self.parameters = parameters

    async def run(self) -> BatchURLCreationInfoV2:
        # Create batch
        command = DBDataCreatorBatchCommand(
            strategy=self.parameters.strategy,
            batch_status=self.parameters.outcome,
            created_at=self.parameters.created_at
        )
        batch_id = self.run_command_sync(command)
        # Return early if batch would not involve URL creation
        if self.parameters.outcome in (BatchStatus.ERROR, BatchStatus.ABORTED):
            return BatchURLCreationInfoV2(
                batch_id=batch_id,
            )

        response = await self.run_command(
            URLsV2Command(
                parameters=self.parameters.urls,
                batch_id=batch_id,
                created_at=self.parameters.created_at
            )
        )

        return BatchURLCreationInfoV2(
            batch_id=batch_id,
            urls_by_status=response.urls_by_status,
        )
