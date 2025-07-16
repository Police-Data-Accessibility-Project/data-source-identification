from http import HTTPStatus
from typing import Optional

from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError

from src.api.endpoints.annotate.agency.get.dto import GetNextURLForAgencyAnnotationResponse
from src.api.endpoints.annotate.agency.post.dto import URLAgencyAnnotationPostInfo
from src.api.endpoints.annotate.all.get.dto import GetNextURLForAllAnnotationResponse
from src.api.endpoints.annotate.all.post.dto import AllAnnotationPostInfo
from src.api.endpoints.annotate.dtos.record_type.response import GetNextRecordTypeAnnotationResponseOuterInfo
from src.api.endpoints.annotate.relevance.get.dto import GetNextRelevanceAnnotationResponseOuterInfo
from src.api.endpoints.batch.dtos.get.duplicates import GetDuplicatesByBatchResponse
from src.api.endpoints.batch.dtos.get.logs import GetBatchLogsResponse
from src.api.endpoints.batch.dtos.get.summaries.response import GetBatchSummariesResponse
from src.api.endpoints.batch.dtos.get.summaries.summary import BatchSummary
from src.api.endpoints.batch.dtos.get.urls import GetURLsByBatchResponse
from src.api.endpoints.batch.dtos.post.abort import MessageResponse
from src.api.endpoints.collector.dtos.collector_start import CollectorStartInfo
from src.api.endpoints.collector.dtos.manual_batch.post import ManualBatchInputDTO
from src.api.endpoints.collector.dtos.manual_batch.response import ManualBatchResponseDTO
from src.api.endpoints.metrics.dtos.get.backlog import GetMetricsBacklogResponseDTO
from src.api.endpoints.metrics.dtos.get.batches.aggregated import GetMetricsBatchesAggregatedResponseDTO
from src.api.endpoints.metrics.dtos.get.batches.breakdown import GetMetricsBatchesBreakdownResponseDTO
from src.api.endpoints.metrics.dtos.get.urls.aggregated.core import GetMetricsURLsAggregatedResponseDTO
from src.api.endpoints.metrics.dtos.get.urls.aggregated.pending import GetMetricsURLsAggregatedPendingResponseDTO
from src.api.endpoints.metrics.dtos.get.urls.breakdown.pending import GetMetricsURLsBreakdownPendingResponseDTO
from src.api.endpoints.metrics.dtos.get.urls.breakdown.submitted import GetMetricsURLsBreakdownSubmittedResponseDTO
from src.api.endpoints.review.approve.dto import FinalReviewApprovalInfo
from src.api.endpoints.review.enums import RejectionReason
from src.api.endpoints.review.next.dto import GetNextURLForFinalReviewOuterResponse
from src.api.endpoints.search.dtos.response import SearchURLResponse
from src.api.endpoints.task.dtos.get.task import TaskInfo
from src.api.endpoints.task.dtos.get.tasks import GetTasksResponse
from src.api.endpoints.url.dtos.response import GetURLsResponseInfo
from src.db.client.async_ import AsyncDatabaseClient
from src.db.dtos.batch import BatchInfo
from src.api.endpoints.task.dtos.get.task_status import GetTaskStatusResponseInfo
from src.db.enums import TaskType
from src.collectors.manager import AsyncCollectorManager
from src.collectors.enums import CollectorType
from src.core.tasks.url.manager import TaskManager
from src.core.error_manager.core import ErrorManager
from src.core.enums import BatchStatus, RecordType, AnnotationType, SuggestedStatus

from src.security.dtos.access_info import AccessInfo


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
    async def get_batch_info(self, batch_id: int) -> BatchSummary:
        result = await self.adb_client.get_batch_by_id(batch_id)
        if result is None:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail=f"Batch {batch_id} does not exist"
            )
        return result

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
    ) -> GetBatchSummariesResponse:
        results = await self.adb_client.get_batch_summaries(
            collector_type=collector_type,
            status=status,
            page=page,
            has_pending_urls=has_pending_urls
        )
        return results

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
    ) -> CollectorStartInfo:
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
        return GetTaskStatusResponseInfo(status=self.task_manager.manager_status)

    async def run_tasks(self):
        await self.task_manager.trigger_task_run()

    async def get_tasks(
            self,
            page: int,
            task_type: TaskType,
            task_status: BatchStatus
    ) -> GetTasksResponse:
        return await self.adb_client.get_tasks(
            page=page,
            task_type=task_type,
            task_status=task_status
        )


    async def get_task_info(self, task_id: int) -> TaskInfo:
        return await self.adb_client.get_task_info(task_id=task_id)


    #region Annotations and Review

    async def submit_url_relevance_annotation(
            self,
            user_id: int,
            url_id: int,
            suggested_status: SuggestedStatus
    ):
        try:
            return await self.adb_client.add_user_relevant_suggestion(
                user_id=user_id,
                url_id=url_id,
                suggested_status=suggested_status
            )
        except IntegrityError:
            return await ErrorManager.raise_annotation_exists_error(
                annotation_type=AnnotationType.RELEVANCE,
                url_id=url_id
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
        try:
            return await self.adb_client.add_user_record_type_suggestion(
                user_id=user_id,
                url_id=url_id,
                record_type=record_type
            )
        except IntegrityError:
            return await ErrorManager.raise_annotation_exists_error(
                annotation_type=AnnotationType.RECORD_TYPE,
                url_id=url_id
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
    ) -> GetNextURLForFinalReviewOuterResponse:
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
            rejection_reason: RejectionReason
    ):
        await self.adb_client.reject_url(
            url_id=url_id,
            user_id=access_info.user_id,
            rejection_reason=rejection_reason
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

    async def get_batches_aggregated_metrics(self) -> GetMetricsBatchesAggregatedResponseDTO:
        return await self.adb_client.get_batches_aggregated_metrics()

    async def get_batches_breakdown_metrics(self, page: int) -> GetMetricsBatchesBreakdownResponseDTO:
        return await self.adb_client.get_batches_breakdown_metrics(page=page)

    async def get_urls_breakdown_submitted_metrics(self) -> GetMetricsURLsBreakdownSubmittedResponseDTO:
        return await self.adb_client.get_urls_breakdown_submitted_metrics()

    async def get_urls_aggregated_metrics(self) -> GetMetricsURLsAggregatedResponseDTO:
        return await self.adb_client.get_urls_aggregated_metrics()

    async def get_urls_breakdown_pending_metrics(self) -> GetMetricsURLsBreakdownPendingResponseDTO:
        return await self.adb_client.get_urls_breakdown_pending_metrics()

    async def get_backlog_metrics(self) -> GetMetricsBacklogResponseDTO:
        return await self.adb_client.get_backlog_metrics()

    async def get_urls_aggregated_pending_metrics(self) -> GetMetricsURLsAggregatedPendingResponseDTO:
        return await self.adb_client.get_urls_aggregated_pending_metrics()