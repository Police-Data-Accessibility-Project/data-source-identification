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
        pass

    async def inner_task_logic(self):
        pass

