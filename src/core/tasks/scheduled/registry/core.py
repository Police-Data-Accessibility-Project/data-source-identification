from datetime import datetime, timedelta
from typing import Awaitable, Callable

from apscheduler.job import Job
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from src.core.tasks.scheduled.registry.convert import convert_interval_enum_to_hours
from src.core.tasks.scheduled.models.entry import ScheduledTaskEntry
from src.db.enums import TaskType


class ScheduledJobRegistry:


    def __init__(self):
        # Main objects
        self.scheduler = AsyncIOScheduler()

        # Jobs
        self._jobs: dict[TaskType, Job] = {}

    async def add_job(
        self,
        func: Callable,
        entry: ScheduledTaskEntry,
        minute_lag: int
    ) -> None:
        """
        Modifies:
            self._jobs
        """
        self._jobs[entry.operator.task_type] = self.scheduler.add_job(
            func,
            trigger=IntervalTrigger(
                hours=convert_interval_enum_to_hours(entry.interval),
                start_date=datetime.now() + timedelta(minutes=minute_lag)
            ),
            misfire_grace_time=60,
            kwargs={"operator": entry.operator}
        )

    def start_scheduler(self) -> None:
        """
        Modifies:
            self.scheduler
        """
        self.scheduler.start()

    def shutdown_scheduler(self) -> None:
        if self.scheduler.running:
            self.scheduler.shutdown()