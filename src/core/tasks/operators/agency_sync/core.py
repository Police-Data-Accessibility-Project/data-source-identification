from src.core.tasks.operators.agency_sync.constants import MAX_SYNC_REQUESTS
from src.core.tasks.operators.agency_sync.exceptions import MaxRequestsExceededError
from src.core.tasks.operators.base import TaskOperatorBase
from src.db.client.async_ import AsyncDatabaseClient
from src.db.enums import TaskType
from src.pdap_api.client import PDAPClient


class SyncAgenciesTaskOperator(TaskOperatorBase):

    def __init__(
        self,
        adb_client: AsyncDatabaseClient,
        pdap_client: PDAPClient
    ):
        super().__init__(adb_client)
        self.pdap_client = pdap_client

    @property
    def task_type(self) -> TaskType:
        return TaskType.SYNC_AGENCIES

    async def meets_task_prerequisites(self):
        return await self.adb_client.last_full_agencies_sync_over_a_day_ago()

    async def inner_task_logic(self):
        params = await self.adb_client.get_agencies_sync_parameters()
        if params.page is None:
            params.page = 1

        response = await self.pdap_client.sync_agencies(params)
        request_count = 1
        while len(response.agencies) > 0:
            if request_count > MAX_SYNC_REQUESTS:
                raise MaxRequestsExceededError(
                    f"Max requests in a single task run ({MAX_SYNC_REQUESTS}) exceeded."
                )
            await self.adb_client.upsert_agencies(response.agencies)

            params.page += 1
            await self.adb_client.update_agencies_sync_progress(params.page)

            response = await self.pdap_client.sync_agencies(params)
            request_count += 1

        await self.adb_client.mark_full_agencies_sync()

        pass

