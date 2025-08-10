from src.core.tasks.scheduled.templates.operator import ScheduledTaskOperatorBase
from src.db.client.async_ import AsyncDatabaseClient
from src.db.enums import TaskType


class DeleteOldLogsTaskOperator(ScheduledTaskOperatorBase):

    def __init__(self, adb_client: AsyncDatabaseClient):
        super().__init__(adb_client)

    @property
    def task_type(self) -> TaskType:
        return TaskType.DELETE_OLD_LOGS

    async def inner_task_logic(self) -> None:
        await self.adb_client.delete_old_logs()