import asyncio
from dataclasses import dataclass

from src.api.endpoints.batch.dtos.get.summaries.response import GetBatchSummariesResponse
from src.core.core import AsyncCore
from src.core.enums import BatchStatus
from tests.automated.integration.api._helpers.RequestValidator import RequestValidator
from tests.helpers.data_creator.core import DBDataCreator


@dataclass
class APITestHelper:
    request_validator: RequestValidator
    async_core: AsyncCore
    db_data_creator: DBDataCreator

    def adb_client(self):
        return self.db_data_creator.adb_client

    async def wait_for_all_batches_to_complete(self):
        for i in range(20):
            data: GetBatchSummariesResponse = self.request_validator.get_batch_statuses(
                status=BatchStatus.IN_PROCESS
            )
            if len(data.results) == 0:
                return
            print("Waiting...")
            await asyncio.sleep(0.1)
        raise ValueError("Batches did not complete in expected time")
