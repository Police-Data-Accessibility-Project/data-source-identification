from http import HTTPStatus
from typing import Optional, Annotated

from pydantic import BaseModel
from starlette.testclient import TestClient

from collector_db.DTOs.BatchInfo import BatchInfo
from collector_manager.DTOs.ExampleInputDTO import ExampleInputDTO
from collector_manager.enums import CollectorType
from core.DTOs.GetBatchLogsResponse import GetBatchLogsResponse
from core.DTOs.GetBatchStatusResponse import GetBatchStatusResponse
from core.DTOs.GetDuplicatesByBatchResponse import GetDuplicatesByBatchResponse
from core.DTOs.GetNextURLForRelevanceAnnotationResponse import GetNextURLForRelevanceAnnotationResponse
from core.DTOs.GetURLsByBatchResponse import GetURLsByBatchResponse
from core.DTOs.LabelStudioExportResponseInfo import LabelStudioExportResponseInfo
from core.DTOs.MessageCountResponse import MessageCountResponse
from core.DTOs.MessageResponse import MessageResponse
from core.DTOs.RelevanceAnnotationInfo import RelevanceAnnotationPostInfo
from core.enums import BatchStatus
from util.helper_functions import update_if_not_none


class ExpectedResponseInfo(BaseModel):
    status_code: Annotated[HTTPStatus, "The expected status code"] = HTTPStatus.OK

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

    def get_batch_statuses(self, collector_type: Optional[CollectorType] = None, status: Optional[BatchStatus] = None) -> GetBatchStatusResponse:
        params = {}
        update_if_not_none(
            target=params,
            source={
                "collector_type": collector_type.value if collector_type else None,
                "status": status.value if status else None
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

    def export_batch_to_label_studio(self, batch_id: int) -> LabelStudioExportResponseInfo:
        data = self.post(
            url=f"/label-studio/export-batch/{batch_id}"
        )
        return LabelStudioExportResponseInfo(**data)

    def abort_batch(self, batch_id: int) -> MessageResponse:
        data = self.post(
            url=f"/batch/{batch_id}/abort"
        )
        return MessageResponse(**data)

    def process_relevancy(self) -> MessageCountResponse:
        # TODO: Delete
        data = self.post(
            url=f"process/relevancy"
        )
        return MessageCountResponse(**data)

    def get_next_relevance_annotation(self) -> GetNextURLForRelevanceAnnotationResponse:
        data = self.get(
            url=f"/annotate/relevance"
        )
        return GetNextURLForRelevanceAnnotationResponse(**data)

    def post_relevance_annotation_and_get_next(
            self,
            metadata_id: int,
            relevance_annotation_post_info: RelevanceAnnotationPostInfo
    ) -> GetNextURLForRelevanceAnnotationResponse:
        data = self.post(
            url=f"/annotate/relevance/{metadata_id}",
            json=relevance_annotation_post_info.model_dump()
        )
        return GetNextURLForRelevanceAnnotationResponse(**data)
