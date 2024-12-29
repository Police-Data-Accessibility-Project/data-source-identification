from http import HTTPMethod, HTTPStatus
from typing import Optional, Annotated

from httpx import Response
from pydantic import BaseModel
from starlette.testclient import TestClient

from collector_db.DTOs.BatchInfo import BatchInfo
from core.DTOs.CollectorStatusResponse import CollectorStatusResponse
from core.DTOs.GetBatchStatusResponse import GetBatchStatusResponse
from core.DTOs.GetStatusResponse import GetStatusResponse


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
        response = self.client.request(method, url, **kwargs)
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

    def get_batch_status(self, batch_id: int) -> GetStatusResponse:
        data = self.get(
            url=f"/collector/status",
            params={"batch_id": batch_id}
        )
        return GetStatusResponse(**data)

    def get_batch_statuses(self) -> GetBatchStatusResponse:
        data = self.get(
            url=f"/batch"
        )
        return GetBatchStatusResponse(**data)

    def get_batch_info(self, batch_id: int) -> BatchInfo:
        data = self.get(
            url=f"/batch/{batch_id}"
        )
        return BatchInfo(**data)
