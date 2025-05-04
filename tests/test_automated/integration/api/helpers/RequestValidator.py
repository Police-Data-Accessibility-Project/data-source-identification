from http import HTTPStatus
from typing import Optional, Annotated

from fastapi import HTTPException
from pydantic import BaseModel
from starlette.testclient import TestClient

from collector_db.DTOs.BatchInfo import BatchInfo
from collector_db.DTOs.GetTaskStatusResponseInfo import GetTaskStatusResponseInfo
from collector_db.DTOs.TaskInfo import TaskInfo
from collector_db.enums import TaskType
from collector_manager.DTOs.ExampleInputDTO import ExampleInputDTO
from collector_manager.enums import CollectorType
from core.DTOs.AllAnnotationPostInfo import AllAnnotationPostInfo
from core.DTOs.FinalReviewApprovalInfo import FinalReviewApprovalInfo, FinalReviewBaseInfo
from core.DTOs.GetBatchLogsResponse import GetBatchLogsResponse
from core.DTOs.GetBatchStatusResponse import GetBatchStatusResponse
from core.DTOs.GetDuplicatesByBatchResponse import GetDuplicatesByBatchResponse
from core.DTOs.GetNextRecordTypeAnnotationResponseInfo import GetNextRecordTypeAnnotationResponseOuterInfo
from core.DTOs.GetNextRelevanceAnnotationResponseInfo import GetNextRelevanceAnnotationResponseOuterInfo
from core.DTOs.GetNextURLForAgencyAnnotationResponse import GetNextURLForAgencyAnnotationResponse, \
    URLAgencyAnnotationPostInfo
from core.DTOs.GetNextURLForAllAnnotationResponse import GetNextURLForAllAnnotationResponse
from core.DTOs.GetNextURLForFinalReviewResponse import GetNextURLForFinalReviewOuterResponse
from core.DTOs.GetTasksResponse import GetTasksResponse
from core.DTOs.GetURLsByBatchResponse import GetURLsByBatchResponse
from core.DTOs.GetURLsResponseInfo import GetURLsResponseInfo
from core.DTOs.ManualBatchInputDTO import ManualBatchInputDTO
from core.DTOs.ManualBatchResponseDTO import ManualBatchResponseDTO
from core.DTOs.MessageResponse import MessageResponse
from core.DTOs.RecordTypeAnnotationPostInfo import RecordTypeAnnotationPostInfo
from core.DTOs.RelevanceAnnotationPostInfo import RelevanceAnnotationPostInfo
from core.DTOs.SearchURLResponse import SearchURLResponse
from core.enums import BatchStatus
from util.helper_functions import update_if_not_none


class ExpectedResponseInfo(BaseModel):
    status_code: Annotated[
        HTTPStatus,
        "The expected status code"
    ] = HTTPStatus.OK
    message: Optional[str] = None

class RequestValidator:
    """
    A class used to assist in API testing.
    Standardizes requests and responses
    and provides means to validate responses

    Also provides common API methods
    """

    def __init__(self, client: TestClient) -> None:
        self.client = client

    def open(
            self,
            method: str,
            url: str,
            params: Optional[dict] = None,
            expected_response: ExpectedResponseInfo = ExpectedResponseInfo(),
            **kwargs
    ) -> dict:
        if params:
            kwargs["params"] = params
        response = self.client.request(
            method=method,
            url=url,
            headers={"Authorization": "Bearer token"},  # Fake authentication that is overridden during testing
            **kwargs)
        assert response.status_code == expected_response.status_code, response.text
        return response.json()

    def open_v2(
            self,
            method: str,
            url: str,
            params: Optional[dict] = None,
            **kwargs
    ) -> dict:
        """
        Variation on open that raises an exception rather than check the status code
        """
        if params:
            kwargs["params"] = params
        response = self.client.request(
            method=method,
            url=url,
            headers={"Authorization": "Bearer token"},  # Fake authentication that is overridden during testing
            **kwargs
        )
        if response.status_code != HTTPStatus.OK:
            raise HTTPException(
                status_code=response.status_code,
                detail=response.json()
            )
        return response.json()

    def get(
            self,
            url: str,
            params: Optional[dict] = None,
            expected_response: ExpectedResponseInfo = ExpectedResponseInfo(),
            **kwargs
    ) -> dict:
        return self.open(
            method="GET",
            url=url,
            params=params,
            expected_response=expected_response,
            **kwargs
        )

    def post(
            self,
            url: str,
            params: Optional[dict] = None,
            expected_response: ExpectedResponseInfo = ExpectedResponseInfo(),
            **kwargs
    ) -> dict:
        return self.open(
            method="POST",
            url=url,
            params=params,
            expected_response=expected_response,
            **kwargs
        )

    def post_v2(
            self,
            url: str,
            params: Optional[dict] = None,
            **kwargs
    ) -> dict:
        return self.open_v2(
            method="POST",
            url=url,
            params=params,
            **kwargs
        )


    def put(
            self,
            url: str,
            params: Optional[dict] = None,
            expected_response: ExpectedResponseInfo = ExpectedResponseInfo(),
            **kwargs
    ) -> dict:
        return self.open(
            method="PUT",
            url=url,
            params=params,
            expected_response=expected_response,
            **kwargs)

    def delete(
            self,
            url: str,
            params: Optional[dict] = None,
            expected_response: ExpectedResponseInfo = ExpectedResponseInfo(),
            **kwargs
    ) -> dict:
        return self.open(
            method="DELETE",
            url=url,
            params=params,
            expected_response=expected_response,
            **kwargs)

    def get_batch_statuses(
            self,
            collector_type: Optional[CollectorType] = None,
            status: Optional[BatchStatus] = None,
            has_pending_urls: Optional[bool] = None
    ) -> GetBatchStatusResponse:
        params = {}
        update_if_not_none(
            target=params,
            source={
                "collector_type": collector_type.value if collector_type else None,
                "status": status.value if status else None,
                "has_pending_urls": has_pending_urls
            }
        )
        data = self.get(
            url=f"/batch",
            params=params
        )
        return GetBatchStatusResponse(**data)

    def example_collector(self, dto: ExampleInputDTO) -> dict:
        data = self.post(
            url="/collector/example",
            json=dto.model_dump()
        )
        return data

    def get_batch_info(self, batch_id: int) -> BatchInfo:
        data = self.get(
            url=f"/batch/{batch_id}"
        )
        return BatchInfo(**data)

    def get_batch_urls(self, batch_id: int, page: int = 1) -> GetURLsByBatchResponse:
        data = self.get(
            url=f"/batch/{batch_id}/urls",
            params={"page": page}
        )
        return GetURLsByBatchResponse(**data)

    def get_batch_url_duplicates(self, batch_id: int, page: int = 1) -> GetDuplicatesByBatchResponse:
        data = self.get(
            url=f"/batch/{batch_id}/duplicates",
            params={"page": page}
        )
        return GetDuplicatesByBatchResponse(**data)

    def get_batch_logs(self, batch_id: int) -> GetBatchLogsResponse:
        data = self.get(
            url=f"/batch/{batch_id}/logs"
        )
        return GetBatchLogsResponse(**data)

    def abort_batch(self, batch_id: int) -> MessageResponse:
        data = self.post(
            url=f"/batch/{batch_id}/abort"
        )
        return MessageResponse(**data)

    def get_next_relevance_annotation(self) -> GetNextRelevanceAnnotationResponseOuterInfo:
        data = self.get(
            url=f"/annotate/relevance"
        )
        return GetNextRelevanceAnnotationResponseOuterInfo(**data)

    def get_next_record_type_annotation(self) -> GetNextRecordTypeAnnotationResponseOuterInfo:
        data = self.get(
            url=f"/annotate/record-type"
        )
        return GetNextRecordTypeAnnotationResponseOuterInfo(**data)

    def post_record_type_annotation_and_get_next(
            self,
            url_id: int,
            record_type_annotation_post_info: RecordTypeAnnotationPostInfo
    ) -> GetNextRecordTypeAnnotationResponseOuterInfo:
        data = self.post(
            url=f"/annotate/record-type/{url_id}",
            json=record_type_annotation_post_info.model_dump(mode='json')
        )
        return GetNextRecordTypeAnnotationResponseOuterInfo(**data)

    def post_relevance_annotation_and_get_next(
            self,
            url_id: int,
            relevance_annotation_post_info: RelevanceAnnotationPostInfo
    ) -> GetNextRelevanceAnnotationResponseOuterInfo:
        data = self.post(
            url=f"/annotate/relevance/{url_id}",
            json=relevance_annotation_post_info.model_dump(mode='json')
        )
        return GetNextRelevanceAnnotationResponseOuterInfo(**data)

    async def get_next_agency_annotation(self) -> GetNextURLForAgencyAnnotationResponse:
        data = self.get(
            url=f"/annotate/agency"
        )
        return GetNextURLForAgencyAnnotationResponse(**data)

    async def post_agency_annotation_and_get_next(
            self,
            url_id: int,
            agency_annotation_post_info: URLAgencyAnnotationPostInfo
    ) -> GetNextURLForAgencyAnnotationResponse:
        data = self.post(
            url=f"/annotate/agency/{url_id}",
            json=agency_annotation_post_info.model_dump(mode='json')
        )
        return GetNextURLForAgencyAnnotationResponse(**data)

    def get_urls(self, page: int = 1, errors: bool = False) -> GetURLsResponseInfo:
        data = self.get(
            url=f"/url",
            params={"page": page, "errors": errors}
        )
        return GetURLsResponseInfo(**data)

    def get_task_info(self, task_id: int) -> TaskInfo:
        data = self.get(
            url=f"/task/{task_id}"
        )
        return TaskInfo(**data)

    def get_tasks(
            self,
            page: int = 1,
            task_type: Optional[TaskType] = None,
            task_status: Optional[BatchStatus] = None
    ) -> GetTasksResponse:
        params = {"page": page}
        update_if_not_none(
            target=params,
            source={
                "task_type": task_type.value if task_type else None,
                "task_status": task_status.value if task_status else None
            }
        )
        data = self.get(
            url=f"/task",
            params=params
        )
        return GetTasksResponse(**data)

    async def review_next_source(self) -> GetNextURLForFinalReviewOuterResponse:
        data = self.get(
            url=f"/review/next-source"
        )
        return GetNextURLForFinalReviewOuterResponse(**data)

    async def approve_and_get_next_source_for_review(
            self,
            approval_info: FinalReviewApprovalInfo
    ) -> GetNextURLForFinalReviewOuterResponse:
        data = self.post(
            url=f"/review/approve-source",
            json=approval_info.model_dump(mode='json')
        )
        return GetNextURLForFinalReviewOuterResponse(**data)

    async def reject_and_get_next_source_for_review(
            self,
            review_info: FinalReviewBaseInfo
    ) -> GetNextURLForFinalReviewOuterResponse:
        data = self.post(
            url=f"/review/reject-source",
            json=review_info.model_dump(mode='json')
        )
        return GetNextURLForFinalReviewOuterResponse(**data)

    async def get_current_task_status(self) -> GetTaskStatusResponseInfo:
        data = self.get(
            url=f"/task/status"
        )
        return GetTaskStatusResponseInfo(**data)

    async def get_next_url_for_all_annotations(
            self,
            batch_id: Optional[int] = None
    ) -> GetNextURLForAllAnnotationResponse:
        params = {}
        update_if_not_none(
            target=params,
            source={"batch_id": batch_id}
        )
        data = self.get(
            url=f"/annotate/all",
            params=params
        )
        return GetNextURLForAllAnnotationResponse(**data)

    async def post_all_annotations_and_get_next(
            self,
            url_id: int,
            all_annotations_post_info: AllAnnotationPostInfo,
            batch_id: Optional[int] = None,
    ) -> GetNextURLForAllAnnotationResponse:
        params = {}
        update_if_not_none(
            target=params,
            source={"batch_id": batch_id}
        )
        data = self.post(
            url=f"/annotate/all/{url_id}",
            params=params,
            json=all_annotations_post_info.model_dump(mode='json')
        )
        return GetNextURLForAllAnnotationResponse(**data)

    async def submit_manual_batch(
            self,
            dto: ManualBatchInputDTO,
    ) -> ManualBatchResponseDTO:
        data = self.post_v2(
            url="/collector/manual",
            json=dto.model_dump(mode='json'),
        )
        return ManualBatchResponseDTO(**data)

    async def search_url(self, url: str) -> SearchURLResponse:
        data = self.get(
            url=f"/search/url",
            params={"url": url}
        )
        return SearchURLResponse(**data)