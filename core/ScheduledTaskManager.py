from datetime import datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from collector_db.DatabaseClient import DatabaseClient
from core.AsyncCore import AsyncCore


class ScheduledTaskManager:

    def __init__(self, db_client: DatabaseClient):
        # Dependencies
        self.db_client = db_client

        # Main objects
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        self.add_scheduled_tasks()

        # Jobs
        self.delete_old_logs_job = None


    def add_scheduled_tasks(self):
        self.delete_old_logs_job = self.scheduler.add_job(
            self.db_client.delete_old_logs,
            trigger=IntervalTrigger(
                days=1,
                start_date=datetime.now() + timedelta(minutes=10)
            )
        )

    def shutdown(self):
        if self.scheduler.running:
            self.scheduler.shutdown()

class AsyncScheduledTaskManager:

    def __init__(self, async_core: AsyncCore):
        # Dependencies
        self.async_core = async_core

        # Main objects
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        self.add_scheduled_tasks()

        # Jobs
        self.run_cycles_job = None

    def add_scheduled_tasks(self):
        self.run_cycles_job = self.scheduler.add_job(
            self.async_core.run_cycles(),
            trigger=IntervalTrigger(
                hours=1,
                start_date=datetime.now() + timedelta(minutes=1)
            )
        )

    def shutdown(self):
        if self.scheduler.running:
            self.scheduler.shutdown()