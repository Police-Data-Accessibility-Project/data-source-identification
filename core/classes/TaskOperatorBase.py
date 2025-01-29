
from abc import ABC, abstractmethod
from collector_db.AsyncDatabaseClient import AsyncDatabaseClient
from collector_db.enums import TaskType
from core.enums import BatchStatus


class TaskOperatorBase(ABC):

    def __init__(self, adb_client: AsyncDatabaseClient):
        self.adb_client = adb_client
        self.task_id = None
        self.tasks_linked = False

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
        await self.adb_client.link_urls_to_task(task_id=self.task_id, url_ids=url_ids)
        self.tasks_linked = True

    async def initiate_task_in_db(self) -> int:
        task_id = await self.adb_client.initiate_task(
            task_type=self.task_type
        )
        return task_id

    async def conclude_task_in_db(self):
        if not self.tasks_linked:
            raise Exception("Task has not been linked to any URLs")
        await self.adb_client.update_task_status(task_id=self.task_id, status=BatchStatus.COMPLETE)

    async def run_task(self):
        if not await self.meets_task_prerequisites():
            print(f"Task {self.task_type.value} does not meet prerequisites. Skipping...")
            return
        self.task_id = await self.initiate_task_in_db()

        try:
            await self.inner_task_logic()
            await self.conclude_task_in_db()
        except Exception as e:
            await self.handle_task_error(e)

    @abstractmethod
    async def inner_task_logic(self):
        raise NotImplementedError

    async def handle_task_error(self, e):
        await self.adb_client.update_task_status(task_id=self.task_id, status=BatchStatus.ERROR)
        await self.adb_client.add_task_error(
            task_id=self.task_id,
            error=str(e)
        )
