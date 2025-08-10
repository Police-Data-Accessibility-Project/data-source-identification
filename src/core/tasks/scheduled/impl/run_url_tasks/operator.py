from src.core.core import AsyncCore
from src.core.tasks.scheduled.templates.operator import ScheduledTaskOperatorBase
from src.db.enums import TaskType


class RunURLTasksTaskOperator(ScheduledTaskOperatorBase):

    def __init__(self, async_core: AsyncCore):
        super().__init__(async_core.adb_client)
        self.async_core = async_core

    @property
    def task_type(self) -> TaskType:
        return TaskType.RUN_URL_TASKS

    async def inner_task_logic(self) -> None:
        await self.async_core.run_tasks()