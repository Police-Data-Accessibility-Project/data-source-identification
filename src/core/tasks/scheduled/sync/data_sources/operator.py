from src.core.tasks.scheduled.templates.operator import ScheduledTaskOperatorBase
from src.core.tasks.scheduled.sync.check import check_max_sync_requests_not_exceeded
from src.core.tasks.scheduled.sync.data_sources.params import DataSourcesSyncParameters
from src.db.client.async_ import AsyncDatabaseClient
from src.db.enums import TaskType
from src.external.pdap.client import PDAPClient


class SyncDataSourcesTaskOperator(ScheduledTaskOperatorBase):

    def __init__(
        self,
        adb_client: AsyncDatabaseClient,
        pdap_client: PDAPClient
    ):
        super().__init__(adb_client)
        self.pdap_client = pdap_client

    @property
    def task_type(self):
        return TaskType.SYNC_DATA_SOURCES

    async def inner_task_logic(self):
        params = await self.adb_client.get_data_sources_sync_parameters()
        if params.page is None:
            params.page = 1

        response = await self.pdap_client.sync_data_sources(params)
        request_count = 1
        while len(response.data_sources) > 0:
            check_max_sync_requests_not_exceeded(request_count)
            await self.adb_client.upsert_urls_from_data_sources(response.data_sources)

            params = DataSourcesSyncParameters(
                page=params.page + 1,
                cutoff_date=params.cutoff_date
            )
            await self.adb_client.update_data_sources_sync_progress(params.page)

            response = await self.pdap_client.sync_data_sources(params)
            request_count += 1

        await self.adb_client.mark_full_data_sources_sync()
