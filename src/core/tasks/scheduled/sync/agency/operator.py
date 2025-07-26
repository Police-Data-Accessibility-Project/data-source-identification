from src.core.tasks.scheduled.sync.check import check_max_sync_requests_not_exceeded
from src.core.tasks.scheduled.sync.agency.dtos.parameters import AgencySyncParameters
from src.core.tasks.scheduled.templates.operator import ScheduledTaskOperatorBase
from src.db.client.async_ import AsyncDatabaseClient
from src.db.enums import TaskType
from src.external.pdap.client import PDAPClient


class SyncAgenciesTaskOperator(ScheduledTaskOperatorBase):

    def __init__(
        self,
        adb_client: AsyncDatabaseClient,
        pdap_client: PDAPClient
    ):
        super().__init__(adb_client)
        self.pdap_client = pdap_client

    @property
    def task_type(self) -> TaskType:  #
        return TaskType.SYNC_AGENCIES

    async def inner_task_logic(self):
        count_agencies_synced = 0
        params = await self.adb_client.get_agencies_sync_parameters()
        if params.page is None:
            params.page = 1

        response = await self.pdap_client.sync_agencies(params)
        count_agencies_synced += len(response.agencies)
        request_count = 1
        while len(response.agencies) > 0:
            check_max_sync_requests_not_exceeded(request_count)
            await self.adb_client.upsert_agencies(response.agencies)

            params = AgencySyncParameters(
                page=params.page + 1,
                cutoff_date=params.cutoff_date
            )
            await self.adb_client.update_agencies_sync_progress(params.page)

            response = await self.pdap_client.sync_agencies(params)
            count_agencies_synced += len(response.agencies)
            request_count += 1

        await self.adb_client.mark_full_agencies_sync()
        print(f"Sync complete. Synced {count_agencies_synced} agencies")

