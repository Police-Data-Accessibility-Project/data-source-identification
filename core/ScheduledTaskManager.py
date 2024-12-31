from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from collector_db.DatabaseClient import DatabaseClient


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
                start_date=datetime.now()
            )
        )

    def shutdown(self):
        self.scheduler.shutdown()