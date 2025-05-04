from typing import Optional

from pydantic import BaseModel

from collector_db.AsyncDatabaseClient import AsyncDatabaseClient
from collector_db.DTOs.BatchInfo import BatchInfo
from collector_db.DTOs.GetTaskStatusResponseInfo import GetTaskStatusResponseInfo
from collector_db.enums import TaskType
from collector_manager.AsyncCollectorManager import AsyncCollectorManager
from collector_manager.enums import CollectorType
from core.DTOs.AllAnnotationPostInfo import AllAnnotationPostInfo
from core.DTOs.CollectorStartInfo import CollectorStartInfo
from core.DTOs.FinalReviewApprovalInfo import FinalReviewApprovalInfo
from core.DTOs.GetBatchLogsResponse import GetBatchLogsResponse
from core.DTOs.GetBatchStatusResponse import GetBatchStatusResponse
from core.DTOs.GetDuplicatesByBatchResponse import GetDuplicatesByBatchResponse
from core.DTOs.GetNextRecordTypeAnnotationResponseInfo import GetNextRecordTypeAnnotationResponseOuterInfo
from core.DTOs.GetNextRelevanceAnnotationResponseInfo import GetNextRelevanceAnnotationResponseOuterInfo
from core.DTOs.GetNextURLForAgencyAnnotationResponse import GetNextURLForAgencyAnnotationResponse, \
    URLAgencyAnnotationPostInfo
from core.DTOs.GetNextURLForAllAnnotationResponse import GetNextURLForAllAnnotationResponse
from core.DTOs.GetTasksResponse import GetTasksResponse
from core.DTOs.GetURLsByBatchResponse import GetURLsByBatchResponse
from core.DTOs.GetURLsResponseInfo import GetURLsResponseInfo
from core.DTOs.ManualBatchInputDTO import ManualBatchInputDTO
from core.DTOs.ManualBatchResponseDTO import ManualBatchResponseDTO
from core.DTOs.MessageResponse import MessageResponse
from core.DTOs.SearchURLResponse import SearchURLResponse
from core.TaskManager import TaskManager
from core.enums import BatchStatus, RecordType

from security_manager.SecurityManager import AccessInfo


class AsyncCore:

    def __init__(
            self,
            adb_client: AsyncDatabaseClient,
            collector_manager: AsyncCollectorManager,
            task_manager: TaskManager
    ):
        self.task_manager = task_manager
        self.adb_client = adb_client

        self.collector_manager = collector_manager


    async def get_urls(self, page: int, errors: bool) -> GetURLsResponseInfo:
        return await self.adb_client.get_urls(page=page, errors=errors)

    async def shutdown(self):
        await self.collector_manager.shutdown_all_collectors()

    #region Batch
    async def get_batch_info(self, batch_id: int) -> BatchInfo:
        return await self.adb_client.get_batch_by_id(batch_id)

    async def get_urls_by_batch(self, batch_id: int, page: int = 1) -> GetURLsByBatchResponse:
        url_infos = await self.adb_client.get_urls_by_batch(batch_id, page)
        return GetURLsByBatchResponse(urls=url_infos)

    async def abort_batch(self, batch_id: int) -> MessageResponse:
        await self.collector_manager.abort_collector_async(cid=batch_id)
        return MessageResponse(message=f"Batch aborted.")

    async def get_duplicate_urls_by_batch(self, batch_id: int, page: int = 1) -> GetDuplicatesByBatchResponse:
        dup_infos = await self.adb_client.get_duplicates_by_batch_id(batch_id, page=page)
        return GetDuplicatesByBatchResponse(duplicates=dup_infos)

    async def get_batch_statuses(
            self,
            collector_type: Optional[CollectorType],
            status: Optional[BatchStatus],
            has_pending_urls: Optional[bool],
            page: int
    ) -> GetBatchStatusResponse:
        results = await self.adb_client.get_recent_batch_status_info(
            collector_type=collector_type,
            status=status,
            page=page,
            has_pending_urls=has_pending_urls
        )
        return GetBatchStatusResponse(results=results)

    async def get_batch_logs(self, batch_id: int) -> GetBatchLogsResponse:
        logs = await self.adb_client.get_logs_by_batch_id(batch_id)
        return GetBatchLogsResponse(logs=logs)

    #endregion

    # region Collector
    async def initiate_collector(
            self,
            collector_type: CollectorType,
            user_id: int,
        dto: Optional[BaseModel] = None,
    ):
        """
        Reserves a batch ID from the database
        and starts the requisite collector
        """

        batch_info = BatchInfo(
            strategy=collector_type.value,
            status=BatchStatus.IN_PROCESS,
            parameters=dto.model_dump(),
            user_id=user_id
        )

        batch_id = await self.adb_client.insert_batch(batch_info)
        await self.collector_manager.start_async_collector(
            collector_type=collector_type,
            batch_id=batch_id,
            dto=dto
        )
        return CollectorStartInfo(
            batch_id=batch_id,
            message=f"Started {collector_type.value} collector."
        )

    # endregion
    async def get_current_task_status(self) -> GetTaskStatusResponseInfo:
        return GetTaskStatusResponseInfo(status=self.task_manager.task_status)

    async def run_tasks(self):
        await self.task_manager.trigger_task_run()

    async def get_tasks(
            self,
            page: int,
            task_type: TaskType,
            task_status: BatchStatus
    ) -> GetTasksResponse:
        return await self.task_manager.get_tasks(
            page=page,
            task_type=task_type,
            task_status=task_status
        )

    async def get_task_info(self, task_id):
        return await self.task_manager.get_task_info(task_id)

    #region Annotations and Review

    async def submit_url_relevance_annotation(
            self,
            user_id: int,
            url_id: int,
            relevant: bool
    ):
        return await self.adb_client.add_user_relevant_suggestion(
            user_id=user_id,
            url_id=url_id,
            relevant=relevant
        )

    async def get_next_url_for_relevance_annotation(
            self,
            user_id: int,
            batch_id: Optional[int]
    ) -> GetNextRelevanceAnnotationResponseOuterInfo:
        next_annotation = await self.adb_client.get_next_url_for_relevance_annotation(
            user_id=user_id,
            batch_id=batch_id
        )
        return GetNextRelevanceAnnotationResponseOuterInfo(
            next_annotation=next_annotation
        )

    async def get_next_url_for_record_type_annotation(
            self,
            user_id: int,
            batch_id: Optional[int]
    ) -> GetNextRecordTypeAnnotationResponseOuterInfo:
        next_annotation = await self.adb_client.get_next_url_for_record_type_annotation(
            user_id=user_id,
            batch_id=batch_id
        )
        return GetNextRecordTypeAnnotationResponseOuterInfo(
            next_annotation=next_annotation
        )

    async def submit_url_record_type_annotation(
            self,
            user_id: int,
            url_id: int,
            record_type: RecordType,
    ):
        await self.adb_client.add_user_record_type_suggestion(
            user_id=user_id,
            url_id=url_id,
            record_type=record_type
        )


    async def get_next_url_agency_for_annotation(
            self,
            user_id: int,
            batch_id: Optional[int]
    ) -> GetNextURLForAgencyAnnotationResponse:
        return await self.adb_client.get_next_url_agency_for_annotation(
            user_id=user_id,
            batch_id=batch_id
        )

    async def submit_url_agency_annotation(
            self,
            user_id: int,
            url_id: int,
            agency_post_info: URLAgencyAnnotationPostInfo
    ) -> GetNextURLForAgencyAnnotationResponse:
        if not agency_post_info.is_new and not agency_post_info.suggested_agency:
            raise ValueError("suggested_agency must be provided if is_new is False")

        if agency_post_info.is_new:
            agency_suggestion_id = None
        else:
            agency_suggestion_id = agency_post_info.suggested_agency
        return await self.adb_client.add_agency_manual_suggestion(
            user_id=user_id,
            url_id=url_id,
            agency_id=agency_suggestion_id,
            is_new=agency_post_info.is_new,
        )

    async def get_next_source_for_review(
            self,
            batch_id: Optional[int]
    ):
        return await self.adb_client.get_next_url_for_final_review(
            batch_id=batch_id
        )

    async def get_next_url_for_all_annotations(
            self,
            batch_id: Optional[int]
    ) -> GetNextURLForAllAnnotationResponse:
        return await self.adb_client.get_next_url_for_all_annotations(
            batch_id=batch_id
        )

    async def submit_url_for_all_annotations(
            self,
            user_id: int,
            url_id: int,
            post_info: AllAnnotationPostInfo
    ):
        await self.adb_client.add_all_annotations_to_url(
            user_id=user_id,
            url_id=url_id,
            post_info=post_info
        )

    async def approve_url(
            self,
            approval_info: FinalReviewApprovalInfo,
            access_info: AccessInfo
    ):
        await self.adb_client.approve_url(
            approval_info=approval_info,
            user_id=access_info.user_id
        )


    async def reject_url(
            self,
            url_id: int,
            access_info: AccessInfo,
    ):
        await self.adb_client.reject_url(
            url_id=url_id,
            user_id=access_info.user_id
        )

    async def upload_manual_batch(
            self,
            dto: ManualBatchInputDTO,
            user_id: int
    ) -> ManualBatchResponseDTO:
        return await self.adb_client.upload_manual_batch(
            user_id=user_id,
            dto=dto
        )

    async def search_for_url(self, url: str) -> SearchURLResponse:
        return await self.adb_client.search_for_url(url)
