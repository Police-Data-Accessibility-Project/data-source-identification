from datetime import datetime, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from core.AsyncCore import AsyncCore

class AsyncScheduledTaskManager:

    def __init__(self, async_core: AsyncCore):
        # Dependencies
        self.async_core = async_core

        # Main objects
        self.scheduler = AsyncIOScheduler()
        self.scheduler.start()
        self.add_scheduled_tasks()

        # Jobs
        self.run_cycles_job = None
        self.delete_logs_job = None
        self.populate_backlog_snapshot_job = None

    def add_scheduled_tasks(self):
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

    def shutdown(self):
        if self.scheduler.running:
            self.scheduler.shutdown()