from http import HTTPStatus
from unittest.mock import MagicMock, AsyncMock

import pytest

from collector_db.enums import TaskType
from collector_db.models import URL, URLErrorInfo, URLDataSource
from collector_manager.enums import URLStatus
from core.DTOs.FinalReviewApprovalInfo import FinalReviewApprovalInfo
from core.DTOs.TaskOperatorRunInfo import TaskOperatorOutcome
from core.classes.task_operators.SubmitApprovedURLTaskOperator import SubmitApprovedURLTaskOperator
from core.enums import RecordType, SubmitResponseStatus
from tests.helpers.DBDataCreator import BatchURLCreationInfo, DBDataCreator
from pdap_api_client.AccessManager import AccessManager
from pdap_api_client.DTOs import RequestInfo, RequestType, ResponseInfo
from pdap_api_client.PDAPClient import PDAPClient


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

@pytest.fixture
def mock_pdap_client() -> PDAPClient:
    mock_access_manager = MagicMock(
        spec=AccessManager
    )
    mock_access_manager.jwt_header = AsyncMock(
        return_value={"Authorization": "Bearer token"}
    )
    pdap_client = PDAPClient(
        access_manager=mock_access_manager
    )
    return pdap_client

async def setup_validated_urls(db_data_creator: DBDataCreator) -> list[str]:
    creation_info: BatchURLCreationInfo = await db_data_creator.batch_and_urls(
        url_count=3,
        with_html_content=True
    )

    url_1 = creation_info.url_ids[0]
    url_2 = creation_info.url_ids[1]
    url_3 = creation_info.url_ids[2]
    await db_data_creator.adb_client.approve_url(
        approval_info=FinalReviewApprovalInfo(
            url_id=url_1,
            record_type=RecordType.ACCIDENT_REPORTS,
            agency_ids=[1, 2],
            name="URL 1 Name",
            description="URL 1 Description",
            record_formats=["Record Format 1", "Record Format 2"],
            data_portal_type="Data Portal Type 1",
            supplying_entity="Supplying Entity 1"
        ),
        user_id=1
    )
    await db_data_creator.adb_client.approve_url(
        approval_info=FinalReviewApprovalInfo(
            url_id=url_2,
            record_type=RecordType.INCARCERATION_RECORDS,
            agency_ids=[3, 4],
            name="URL 2 Name",
            description="URL 2 Description",
        ),
        user_id=2
    )
    await db_data_creator.adb_client.approve_url(
        approval_info=FinalReviewApprovalInfo(
            url_id=url_3,
            record_type=RecordType.ACCIDENT_REPORTS,
            agency_ids=[5, 6],
            name="URL 3 Name",
            description="URL 3 Description",
        ),
        user_id=3
    )
    return creation_info.urls

@pytest.mark.asyncio
async def test_submit_approved_url_task(
        db_data_creator,
        mock_pdap_client: PDAPClient,
        monkeypatch
):
    """
    The submit_approved_url_task should submit
    all validated URLs to the PDAP Data Sources App
    """


    # Get Task Operator
    operator = SubmitApprovedURLTaskOperator(
        adb_client=db_data_creator.adb_client,
        pdap_client=mock_pdap_client
    )

    # Check Task Operator does not yet meet pre-requisites
    assert not await operator.meets_task_prerequisites()

    # Create URLs with status 'validated' in database and all requisite URL values
    # Ensure they have optional metadata as well
    urls = await setup_validated_urls(db_data_creator)
    mock_make_request(mock_pdap_client, urls)

    # Check Task Operator does meet pre-requisites
    assert await operator.meets_task_prerequisites()

    # Run Task
    task_id = await db_data_creator.adb_client.initiate_task(
        task_type=TaskType.SUBMIT_APPROVED
    )
    run_info = await operator.run_task(task_id=task_id)

    # Check Task has been marked as completed
    assert run_info.outcome == TaskOperatorOutcome.SUCCESS, run_info.message

    # Get URLs
    urls = await db_data_creator.adb_client.get_all(URL, order_by_attribute="id")
    url_1 = urls[0]
    url_2 = urls[1]
    url_3 = urls[2]

    # Check URLs have been marked as 'submitted'
    assert url_1.outcome == URLStatus.SUBMITTED.value
    assert url_2.outcome == URLStatus.SUBMITTED.value
    assert url_3.outcome == URLStatus.ERROR.value

    # Get URL Data Source Links
    url_data_sources = await db_data_creator.adb_client.get_all(URLDataSource)
    assert len(url_data_sources) == 2

    url_data_source_1 = url_data_sources[0]
    url_data_source_2 = url_data_sources[1]

    assert url_data_source_1.url_id == url_1.id
    assert url_data_source_1.data_source_id == 21

    assert url_data_source_2.url_id == url_2.id
    assert url_data_source_2.data_source_id == 34

    # Check that errored URL has entry in url_error_info
    url_errors = await db_data_creator.adb_client.get_all(URLErrorInfo)
    assert len(url_errors) == 1
    url_error = url_errors[0]
    assert url_error.url_id == url_3.id
    assert url_error.error == "Test Error"

    # Check mock method was called expected parameters
    access_manager = mock_pdap_client.access_manager
    access_manager.make_request.assert_called_once()

    call_1 = access_manager.make_request.call_args_list[0][0][0]
    expected_call_1 = RequestInfo(
        type_=RequestType.POST,
        url="TEST/source-collector/data-sources",
        headers=access_manager.jwt_header.return_value,
        json={
            "data_sources": [
                {
                    "name": "URL 1 Name",
                    "source_url": url_1.url,
                    "record_type": "Accident Reports",
                    "description": "URL 1 Description",
                    "record_formats": ["Record Format 1", "Record Format 2"],
                    "data_portal_type": "Data Portal Type 1",
                    "last_approval_editor": 1,
                    "supplying_entity": "Supplying Entity 1",
                    "agency_ids": [1, 2]
                },
                {
                    "name": "URL 2 Name",
                    "source_url": url_2.url,
                    "record_type": "Incarceration Records",
                    "description": "URL 2 Description",
                    "last_approval_editor": 2,
                    "supplying_entity": None,
                    "record_formats": None,
                    "data_portal_type": None,
                    "agency_ids": [3, 4]
                },
                {
                    "name": "URL 3 Name",
                    "source_url": url_3.url,
                    "record_type": "Accident Reports",
                    "description": "URL 3 Description",
                    "last_approval_editor": 3,
                    "supplying_entity": None,
                    "record_formats": None,
                    "data_portal_type": None,
                    "agency_ids": [5, 6]
                }
            ]
        }
    )
    assert call_1.type_ == expected_call_1.type_
    assert call_1.url == expected_call_1.url
    assert call_1.headers == expected_call_1.headers
    assert call_1.json == expected_call_1.json
