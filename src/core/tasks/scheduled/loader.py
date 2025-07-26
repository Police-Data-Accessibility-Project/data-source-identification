from src.core.tasks.scheduled.sync.agency.operator import SyncAgenciesTaskOperator
from src.core.tasks.scheduled.sync.data_sources.operator import SyncDataSourcesTaskOperator
from src.db.client.async_ import AsyncDatabaseClient
from src.external.pdap.client import PDAPClient


class ScheduledTaskOperatorLoader:

    def __init__(
            self,
            adb_client: AsyncDatabaseClient,
            pdap_client: PDAPClient,
    ):
        # Dependencies
        self.adb_client = adb_client
        self.pdap_client = pdap_client


    async def get_sync_agencies_task_operator(self) -> SyncAgenciesTaskOperator:
        return SyncAgenciesTaskOperator(
            adb_client=self.adb_client,
            pdap_client=self.pdap_client
        )

    async def get_sync_data_sources_task_operator(self) -> SyncDataSourcesTaskOperator:
        return SyncDataSourcesTaskOperator(
            adb_client=self.adb_client,
            pdap_client=self.pdap_client
        )
