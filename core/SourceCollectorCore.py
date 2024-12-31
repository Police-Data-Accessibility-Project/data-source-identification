from typing import Optional, List

from pydantic import BaseModel

from collector_db.DTOs.BatchInfo import BatchInfo
from collector_db.DatabaseClient import DatabaseClient
from collector_manager.CollectorManager import CollectorManager
from collector_manager.enums import CollectorType
from core.CoreLogger import CoreLogger
from core.DTOs.CollectorStartInfo import CollectorStartInfo
from core.DTOs.GetBatchLogsResponse import GetBatchLogsResponse
from core.DTOs.GetBatchStatusResponse import GetBatchStatusResponse
from core.DTOs.GetDuplicatesByBatchResponse import GetDuplicatesByBatchResponse
from core.DTOs.GetURLsByBatchResponse import GetURLsByBatchResponse
from core.DTOs.LabelStudioExportResponseInfo import LabelStudioExportResponseInfo
from core.ScheduledTaskManager import ScheduledTaskManager
from core.enums import BatchStatus
from label_studio_interface.DTOs.LabelStudioTaskExportInfo import LabelStudioTaskExportInfo
from label_studio_interface.LabelStudioAPIManager import LabelStudioAPIManager


class SourceCollectorCore:
    def __init__(
        self,
        core_logger: CoreLogger,
        db_client: DatabaseClient = DatabaseClient(),
        label_studio_api_manager: LabelStudioAPIManager = LabelStudioAPIManager(),
        dev_mode: bool = False
    ):
        self.db_client = db_client
        self.collector_manager = CollectorManager(
            logger=core_logger
        )
        if not dev_mode:
            self.scheduled_task_manager = ScheduledTaskManager(db_client=db_client)
        else:
            self.scheduled_task_manager = None
        self.label_studio_api_manager = label_studio_api_manager

    def get_batch_info(self, batch_id: int) -> BatchInfo:
        return self.db_client.get_batch_by_id(batch_id)

    def get_urls_by_batch(self, batch_id: int) -> GetURLsByBatchResponse:
        url_infos = self.db_client.get_urls_by_batch(batch_id)
        return GetURLsByBatchResponse(urls=url_infos)

    def get_duplicate_urls_by_batch(self, batch_id: int) -> GetDuplicatesByBatchResponse:
        dup_infos = self.db_client.get_duplicates_by_batch_id(batch_id)
        return GetDuplicatesByBatchResponse(duplicates=dup_infos)

    def get_batch_statuses(
            self,
            collector_type: Optional[CollectorType],
            status: Optional[BatchStatus],
            limit: int
    ) -> GetBatchStatusResponse:
        results = self.db_client.get_recent_batch_status_info(
            collector_type=collector_type,
            status=status,
            limit=limit
        )
        return GetBatchStatusResponse(results=results)

    def get_status(self, batch_id: int) -> BatchStatus:
        return self.db_client.get_batch_status(batch_id)

    def initiate_collector(
            self,
            collector_type: CollectorType,
            dto: Optional[BaseModel] = None,):
        """
        Reserves a batch ID from the database
        and starts the requisite collector
        """
        batch_info = BatchInfo(
            strategy=collector_type.value,
            status=BatchStatus.IN_PROCESS,
            parameters=dto.model_dump()
        )
        batch_id = self.db_client.insert_batch(batch_info)
        self.collector_manager.start_collector(
            collector_type=collector_type,
            batch_id=batch_id,
            dto=dto
        )
        return CollectorStartInfo(
            batch_id=batch_id,
            message=f"Started {collector_type.value} collector."
        )

    def get_batch_logs(self, batch_id: int) -> GetBatchLogsResponse:
        logs = self.db_client.get_logs_by_batch_id(batch_id)
        return GetBatchLogsResponse(logs=logs)

    def export_batch_to_label_studio(self, batch_id: int) -> LabelStudioExportResponseInfo:
        # TODO: Might this need to be a separate thread?
        db_url_infos = self.db_client.get_urls_by_batch(batch_id)
        url_count = len(db_url_infos)
        export_infos = []
        for url_info in db_url_infos:
            export_infos.append(LabelStudioTaskExportInfo(url=url_info.url))
        import_id = self.label_studio_api_manager.export_tasks_into_project(
            data=export_infos
        )
        return LabelStudioExportResponseInfo(
            label_studio_import_id=import_id,
            num_urls_imported=url_count
        )


    def shutdown(self):
        self.collector_manager.shutdown_all_collectors()
        self.collector_manager.logger.shutdown()
        if self.scheduled_task_manager is not None:
            self.scheduled_task_manager.shutdown()





"""
TODO: Add logic for batch processing

"""