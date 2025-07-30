from datetime import datetime, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from src.core.core import AsyncCore
from src.core.tasks.base.run_info import TaskOperatorRunInfo
from src.core.tasks.handler import TaskHandler
from src.core.tasks.scheduled.loader import ScheduledTaskOperatorLoader
from src.core.tasks.scheduled.templates.operator import ScheduledTaskOperatorBase


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
        self.run_cycles_job = None
        self.delete_logs_job = None
        self.populate_backlog_snapshot_job = None
        self.sync_agencies_job = None
        self.sync_data_sources_job = None
        self.push_to_hugging_face_job = None

    async def setup(self):
        self.scheduler.start()
        await self.add_scheduled_tasks()

    async def add_scheduled_tasks(self):
        self.run_cycles_job = self.scheduler.add_job(
            self.async_core.run_tasks,
            trigger=IntervalTrigger(
                hours=1,
                start_date=datetime.now() + timedelta(minutes=1)
            ),
            misfire_grace_time=60
        )
        self.delete_logs_job = self.scheduler.add_job(
            self.async_core.adb_client.delete_old_logs,
            trigger=IntervalTrigger(
                days=1,
                start_date=datetime.now() + timedelta(minutes=10)
            )
        )
        self.populate_backlog_snapshot_job = self.scheduler.add_job(
            self.async_core.adb_client.populate_backlog_snapshot,
            trigger=IntervalTrigger(
                days=1,
                start_date=datetime.now() + timedelta(minutes=20)
            )
        )
        self.sync_agencies_job = self.scheduler.add_job(
            self.run_task,
            trigger=IntervalTrigger(
                days=1,
                start_date=datetime.now() + timedelta(minutes=2)
            ),
            kwargs={
                "operator": await self.loader.get_sync_agencies_task_operator()
            }
        )
        self.sync_data_sources_job = self.scheduler.add_job(
            self.run_task,
            trigger=IntervalTrigger(
                days=1,
                start_date=datetime.now() + timedelta(minutes=3)
            ),
            kwargs={
                "operator": await self.loader.get_sync_data_sources_task_operator()
            }
        )
        # TODO: enable once more URLs with HTML have been added to the database.
        # self.push_to_hugging_face_job = self.scheduler.add_job(
        #     self.run_task,
        #     trigger=IntervalTrigger(
        #         days=1,
        #         start_date=datetime.now() + timedelta(minutes=4)
        #     ),
        #     kwargs={
        #         "operator": await self.loader.get_push_to_hugging_face_task_operator()
        #     }
        # )

    def shutdown(self):
        if self.scheduler.running:
            self.scheduler.shutdown()

    async def run_task(self, operator: ScheduledTaskOperatorBase):
        print(f"Running {operator.task_type.value} Task")
        task_id = await self.handler.initiate_task_in_db(task_type=operator.task_type)
        run_info: TaskOperatorRunInfo = await operator.run_task(task_id)
        await self.handler.handle_outcome(run_info)
