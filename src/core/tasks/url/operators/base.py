import traceback
from abc import ABC, abstractmethod

from src.core.tasks.base.operator import TaskOperatorBase
from src.db.client.async_ import AsyncDatabaseClient
from src.db.enums import TaskType
from src.core.tasks.dtos.run_info import URLTaskOperatorRunInfo
from src.core.tasks.url.enums import TaskOperatorOutcome
from src.core.enums import BatchStatus


class URLTaskOperatorBase(TaskOperatorBase):

    def __init__(self, adb_client: AsyncDatabaseClient):
        super().__init__(adb_client)
        self.tasks_linked = False
        self.linked_url_ids = []

    @abstractmethod
    async def meets_task_prerequisites(self):
        """
        A task should not be initiated unless certain
        conditions are met
        """
        raise NotImplementedError

    async def link_urls_to_task(self, url_ids: list[int]):
        self.linked_url_ids = url_ids

    async def conclude_task(self):
        if not self.linked_url_ids:
            raise Exception("Task has not been linked to any URLs")
        return await self.run_info(
            outcome=TaskOperatorOutcome.SUCCESS,
            message="Task completed successfully"
        )

    async def run_task(self, task_id: int) -> URLTaskOperatorRunInfo:
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

    async def run_info(
        self,
        outcome: TaskOperatorOutcome,
        message: str
    ) -> URLTaskOperatorRunInfo:
        return URLTaskOperatorRunInfo(
            task_id=self.task_id,
            task_type=self.task_type,
            linked_url_ids=self.linked_url_ids,
            outcome=outcome,
            message=message
        )
