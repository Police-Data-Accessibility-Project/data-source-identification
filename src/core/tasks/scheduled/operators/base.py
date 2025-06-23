from abc import abstractmethod

from src.core.tasks.base.operator import TaskOperatorBase
from src.core.tasks.base.run_info import TaskOperatorRunInfo
from src.core.tasks.url.enums import TaskOperatorOutcome
from src.db.enums import TaskType


class ScheduledTaskOperatorBase(TaskOperatorBase):

    @property
    @abstractmethod
    def task_type(self) -> TaskType:
        raise NotImplementedError

    async def conclude_task(self):
        return await self.run_info(
            outcome=TaskOperatorOutcome.SUCCESS,
            message="Task completed successfully"
        )

    async def run_info(
        self,
        outcome: TaskOperatorOutcome,
        message: str
    ) -> TaskOperatorRunInfo:
        return TaskOperatorRunInfo(
            task_id=self.task_id,
            task_type=self.task_type,
            outcome=outcome,
            message=message
        )
