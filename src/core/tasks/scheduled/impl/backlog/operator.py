from src.core.tasks.scheduled.templates.operator import ScheduledTaskOperatorBase
from src.db.client.async_ import AsyncDatabaseClient
from src.db.enums import TaskType


class PopulateBacklogSnapshotTaskOperator(ScheduledTaskOperatorBase):

    def __init__(self, adb_client: AsyncDatabaseClient):
        super().__init__(adb_client)

    @property
    def task_type(self) -> TaskType:
        return TaskType.POPULATE_BACKLOG_SNAPSHOT

    async def inner_task_logic(self) -> None:
        await self.adb_client.populate_backlog_snapshot()