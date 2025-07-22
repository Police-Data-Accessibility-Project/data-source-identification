from src.core.tasks.scheduled.operators.agency_sync.core import SyncAgenciesTaskOperator
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


    async def get_sync_agencies_task_operator(self):
        operator = SyncAgenciesTaskOperator(
            adb_client=self.adb_client,
            pdap_client=self.pdap_client
        )
        return operator