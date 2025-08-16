import traceback
from abc import ABC, abstractmethod

from src.core.enums import BatchStatus
from src.core.tasks.base.run_info import TaskOperatorRunInfo
from src.core.tasks.url.enums import TaskOperatorOutcome
from src.db.client.async_ import AsyncDatabaseClient
from src.db.enums import TaskType


class TaskOperatorBase(ABC):
    def __init__(self, adb_client: AsyncDatabaseClient):
        self.adb_client = adb_client
        self.task_id = None

    @property
    @abstractmethod
    def task_type(self) -> TaskType:
        raise NotImplementedError

    async def initiate_task_in_db(self) -> int:
        task_id = await self.adb_client.initiate_task(
            task_type=self.task_type
        )
        return task_id

    @abstractmethod
    async def conclude_task(self):
        raise NotImplementedError

    async def run_task(self, task_id: int) -> TaskOperatorRunInfo:
        self.task_id = task_id
        try:
            await self.inner_task_logic()
            return await self.conclude_task()
        except Exception as e:
            stack_trace = traceback.format_exc()
            return await self.run_info(
                outcome=TaskOperatorOutcome.ERROR,
                message=str(e) + "\n" + stack_trace
            )

    @abstractmethod
    async def run_info(self, outcome: TaskOperatorOutcome, message: str) -> TaskOperatorRunInfo:
        raise NotImplementedError


    @abstractmethod
    async def inner_task_logic(self) -> None:
        raise NotImplementedError

    async def handle_task_error(self, e):
        await self.adb_client.update_task_status(task_id=self.task_id, status=BatchStatus.ERROR)
        await self.adb_client.add_task_error(
            task_id=self.task_id,
            error=str(e)
        )
