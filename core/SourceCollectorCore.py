from typing import Optional, Any


from collector_db.DatabaseClient import DatabaseClient
from collector_manager.enums import CollectorType
from core.DTOs.GetBatchLogsResponse import GetBatchLogsResponse
from core.DTOs.GetBatchStatusResponse import GetBatchStatusResponse
from core.DTOs.GetDuplicatesByBatchResponse import GetDuplicatesByBatchResponse
from core.ScheduledTaskManager import ScheduledTaskManager
from core.enums import BatchStatus


class SourceCollectorCore:
    def __init__(
        self,
        core_logger: Optional[Any] = None,  # Deprecated
        collector_manager: Optional[Any] = None,  # Deprecated
        db_client: DatabaseClient = DatabaseClient(),
        dev_mode: bool = False
    ):
        self.db_client = db_client
        if not dev_mode:
            self.scheduled_task_manager = ScheduledTaskManager(db_client=db_client)
        else:
            self.scheduled_task_manager = None

    def get_duplicate_urls_by_batch(self, batch_id: int, page: int = 1) -> GetDuplicatesByBatchResponse:
        dup_infos = self.db_client.get_duplicates_by_batch_id(batch_id, page=page)
        return GetDuplicatesByBatchResponse(duplicates=dup_infos)

    def get_batch_statuses(
            self,
            collector_type: Optional[CollectorType],
            status: Optional[BatchStatus],
            page: int
    ) -> GetBatchStatusResponse:
        results = self.db_client.get_recent_batch_status_info(
            collector_type=collector_type,
            status=status,
            page=page
        )
        return GetBatchStatusResponse(results=results)

    def get_status(self, batch_id: int) -> BatchStatus:
        return self.db_client.get_batch_status(batch_id)

    def get_batch_logs(self, batch_id: int) -> GetBatchLogsResponse:
        logs = self.db_client.get_logs_by_batch_id(batch_id)
        return GetBatchLogsResponse(logs=logs)

    def shutdown(self):
        if self.scheduled_task_manager is not None:
            self.scheduled_task_manager.shutdown()





"""
TODO: Add logic for batch processing

"""