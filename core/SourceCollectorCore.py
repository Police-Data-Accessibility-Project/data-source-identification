from typing import Optional, List

from pydantic import BaseModel

from collector_db.DTOs.BatchInfo import BatchInfo
from collector_db.DatabaseClient import DatabaseClient
from collector_manager.CollectorManager import CollectorManager
from collector_manager.enums import CollectorType
from core.CoreLogger import CoreLogger
from core.DTOs.CollectorStartInfo import CollectorStartInfo
from core.DTOs.GetBatchStatusResponse import GetBatchStatusResponse
from core.enums import BatchStatus


class SourceCollectorCore:
    def __init__(
        self,
        core_logger: CoreLogger,
        db_client: DatabaseClient = DatabaseClient(),
    ):
        self.db_client = db_client
        self.collector_manager = CollectorManager(
            logger=core_logger
        )

    def get_batch_info(self, batch_id: int) -> BatchInfo:
        return self.db_client.get_batch_by_id(batch_id)

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





"""
TODO: Add logic for batch processing

"""