from apscheduler.job import Job
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.core.tasks.base.run_info import TaskOperatorRunInfo
from src.core.tasks.handler import TaskHandler
from src.core.tasks.scheduled.loader import ScheduledTaskOperatorLoader
from src.core.tasks.scheduled.models.entry import ScheduledTaskEntry
from src.core.tasks.scheduled.registry.core import ScheduledJobRegistry
from src.core.tasks.scheduled.templates.operator import ScheduledTaskOperatorBase


class AsyncScheduledTaskManager:

    def __init__(
        self,
        handler: TaskHandler,
        loader: ScheduledTaskOperatorLoader,
        registry: ScheduledJobRegistry
    ):

        # Dependencies
        self._handler = handler
        self._loader = loader
        self._registry = registry

        # Main objects
        self.scheduler = AsyncIOScheduler()


    async def setup(self):
        self._registry.start_scheduler()
        await self.add_scheduled_tasks()

    async def add_scheduled_tasks(self):
        """
        Modifies:
            self._registry
        """
        entries: list[ScheduledTaskEntry] = await self._loader.load_entries()
        for idx, entry in enumerate(entries):
            if not entry.enabled:
                print(f"{entry.operator.task_type.value} is disabled. Skipping add to scheduler.")
                continue

            await self._registry.add_job(
                func=self.run_task,
                entry=entry,
                minute_lag=idx
            )

    def shutdown(self):
        self._registry.shutdown_scheduler()

    async def run_task(self, operator: ScheduledTaskOperatorBase):
        print(f"Running {operator.task_type.value} Task")
        task_id = await self._handler.initiate_task_in_db(task_type=operator.task_type)
        run_info: TaskOperatorRunInfo = await operator.run_task(task_id)
        await self._handler.handle_outcome(run_info)
