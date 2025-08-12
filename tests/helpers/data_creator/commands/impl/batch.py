from datetime import datetime
from typing import Optional

from src.collectors.enums import CollectorType
from src.core.enums import BatchStatus
from src.db.models.impl.batch.pydantic import BatchInfo
from tests.helpers.data_creator.commands.base import DBDataCreatorCommandBase


class DBDataCreatorBatchCommand(DBDataCreatorCommandBase):

    def __init__(
        self,
        strategy: CollectorType = CollectorType.EXAMPLE,
        batch_status: BatchStatus = BatchStatus.IN_PROCESS,
        created_at: Optional[datetime] = None
    ):
        super().__init__()
        self.strategy = strategy
        self.batch_status = batch_status
        self.created_at = created_at

    async def run(self) -> int:
        raise NotImplementedError

    def run_sync(self) -> int:
        return self.db_client.insert_batch(
            BatchInfo(
                strategy=self.strategy.value,
                status=self.batch_status,
                parameters={"test_key": "test_value"},
                user_id=1,
                date_generated=self.created_at
            )
        )