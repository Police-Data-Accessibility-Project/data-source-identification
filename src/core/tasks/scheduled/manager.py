from datetime import datetime, timedelta

from apscheduler.job import Job
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from src.core.core import AsyncCore
from src.core.tasks.base.run_info import TaskOperatorRunInfo
from src.core.tasks.handler import TaskHandler
from src.core.tasks.scheduled.convert import convert_interval_enum_to_hours
from src.core.tasks.scheduled.enums import IntervalEnum
from src.core.tasks.scheduled.loader import ScheduledTaskOperatorLoader
from src.core.tasks.scheduled.models.entry import ScheduledTaskEntry
from src.core.tasks.scheduled.templates.operator import ScheduledTaskOperatorBase

from environs import Env


class AsyncScheduledTaskManager:

    def __init__(
        self,
        async_core: AsyncCore,
        handler: TaskHandler,
        loader: ScheduledTaskOperatorLoader
    ):
        # Dependencies
        self.async_core = async_core
        self.handler = handler
        self.loader = loader

        # Main objects
        self.scheduler = AsyncIOScheduler()

        # Jobs
        self._jobs: dict[str, Job] = {}


    async def setup(self):
        env = Env()
        env.read_env()

        scheduled_task_flag = env.bool("SCHEDULED_TASKS_FLAG", default=True)
        if not scheduled_task_flag:
            print("Scheduled tasks are disabled.")
            return

        self.scheduler.start()
        await self.add_scheduled_tasks()

    async def _get_entries(self) -> list[ScheduledTaskEntry]:
        return [
            ScheduledTaskEntry(
                name="Run Task Cycles",
                function=self.async_core.run_tasks,
                interval=IntervalEnum.HOURLY
            ),
            ScheduledTaskEntry(
                name="Delete Old Logs",
                function=self.async_core.adb_client.delete_old_logs,
                interval=IntervalEnum.DAILY
            ),
            ScheduledTaskEntry(
                name="Populate Backlog Snapshot",
                function=self.async_core.adb_client.populate_backlog_snapshot,
                interval=IntervalEnum.DAILY
            ),
            ScheduledTaskEntry(
                name="Sync Agencies",
                function=self.run_task,
                interval=IntervalEnum.DAILY,
                kwargs={
                    "operator": await self.loader.get_sync_agencies_task_operator()
                }
            ),
            ScheduledTaskEntry(
                name="Sync Data Sources",
                function=self.run_task,
                interval=IntervalEnum.DAILY,
                kwargs={
                    "operator": await self.loader.get_sync_data_sources_task_operator()
                }
            ),
            # ScheduledTaskEntry(
            #     name="Push to Hugging Face",
            #     function=self.run_task,
            #     interval=IntervalEnum.DAILY,
            #     kwargs={
            #         "operator": await self.loader.get_push_to_hugging_face_task_operator()
            #     }
            # )
        ]

    async def add_scheduled_tasks(self):
        """
        Modifies:
            self._jobs
        """
        entries: list[ScheduledTaskEntry] = await self._get_entries()
        for idx, entry in enumerate(entries):
            self._jobs[entry.name] = self.scheduler.add_job(
                entry.function,
                trigger=IntervalTrigger(
                    hours=convert_interval_enum_to_hours(entry.interval),
                    start_date=datetime.now() + timedelta(minutes=idx + 1)
                ),
                misfire_grace_time=60,
                kwargs=entry.kwargs
            )

    def shutdown(self):
        if self.scheduler.running:
            self.scheduler.shutdown()

    async def run_task(self, operator: ScheduledTaskOperatorBase):
        print(f"Running {operator.task_type.value} Task")
        task_id = await self.handler.initiate_task_in_db(task_type=operator.task_type)
        run_info: TaskOperatorRunInfo = await operator.run_task(task_id)
        await self.handler.handle_outcome(run_info)
