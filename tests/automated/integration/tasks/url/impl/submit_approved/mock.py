from http import HTTPStatus
from unittest.mock import AsyncMock

from pdap_access_manager import ResponseInfo

from src.core.enums import SubmitResponseStatus
from src.external.pdap.client import PDAPClient


def mock_make_request(pdap_client: PDAPClient, urls: list[str]):
    assert len(urls) == 3, "Expected 3 urls"
    pdap_client.access_manager.make_request = AsyncMock(
        return_value=ResponseInfo(
            status_code=HTTPStatus.OK,
            data={
                "data_sources": [
                    {
                        "url": urls[0],
                        "status": SubmitResponseStatus.SUCCESS,
                        "error": None,
                        "data_source_id": 21,
                    },
                    {
                        "url": urls[1],
                        "status": SubmitResponseStatus.SUCCESS,
                        "error": None,
                        "data_source_id": 34,
                    },
                    {
                        "url": urls[2],
                        "status": SubmitResponseStatus.FAILURE,
                        "error": "Test Error",
                        "data_source_id": None
                    }
                ]
            }
        )
    )
