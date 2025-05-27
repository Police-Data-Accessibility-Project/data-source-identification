import traceback
from abc import ABC, abstractmethod
from db.AsyncDatabaseClient import AsyncDatabaseClient
from db.enums import TaskType
from core.DTOs.TaskOperatorRunInfo import TaskOperatorOutcome, TaskOperatorRunInfo
from core.enums import BatchStatus


class TaskOperatorBase(ABC):

    def __init__(self, adb_client: AsyncDatabaseClient):
        self.adb_client = adb_client
        self.task_id = None
        self.tasks_linked = False
        self.linked_url_ids = []

    @property
    @abstractmethod
    def task_type(self) -> TaskType:
        raise NotImplementedError

    @abstractmethod
    async def meets_task_prerequisites(self):
        """
        A task should not be initiated unless certain
        conditions are met
        """
        raise NotImplementedError

    async def link_urls_to_task(self, url_ids: list[int]):
        self.linked_url_ids = url_ids

    async def initiate_task_in_db(self) -> int:
        task_id = await self.adb_client.initiate_task(
            task_type=self.task_type
        )
        return task_id

    async def conclude_task(self):
        if not self.linked_url_ids:
            raise Exception("Task has not been linked to any URLs")
        return await self.run_info(
            outcome=TaskOperatorOutcome.SUCCESS,
            message="Task completed successfully"
        )

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

    async def run_info(self, outcome: TaskOperatorOutcome, message: str):
        return TaskOperatorRunInfo(
            task_id=self.task_id,
            linked_url_ids=self.linked_url_ids,
            outcome=outcome,
            message=message
        )

    @abstractmethod
    async def inner_task_logic(self):
        raise NotImplementedError

    async def handle_task_error(self, e):
        await self.adb_client.update_task_status(task_id=self.task_id, status=BatchStatus.ERROR)
        await self.adb_client.add_task_error(
            task_id=self.task_id,
            error=str(e)
        )
