from typing import Optional, Any


from collector_db.DatabaseClient import DatabaseClient
from core.ScheduledTaskManager import ScheduledTaskManager
from core.enums import BatchStatus


class SourceCollectorCore:
    def __init__(
        self,
        core_logger: Optional[Any] = None,  # Deprecated
        collector_manager: Optional[Any] = None,  # Deprecated
        db_client: Optional[DatabaseClient] = None,
        dev_mode: bool = False
    ):
        if db_client is None:
            db_client = DatabaseClient()
        self.db_client = db_client
        if not dev_mode:
            self.scheduled_task_manager = ScheduledTaskManager(db_client=db_client)
        else:
            self.scheduled_task_manager = None


    def get_status(self, batch_id: int) -> BatchStatus:
        return self.db_client.get_batch_status(batch_id)


    def shutdown(self):
        if self.scheduled_task_manager is not None:
            self.scheduled_task_manager.shutdown()





"""
TODO: Add logic for batch processing

"""