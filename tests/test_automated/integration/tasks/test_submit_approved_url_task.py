from http import HTTPStatus
from unittest.mock import MagicMock, AsyncMock

import pytest

from collector_db.models import URL
from collector_manager.enums import URLStatus
from core.DTOs.FinalReviewApprovalInfo import FinalReviewApprovalInfo
from core.DTOs.TaskOperatorRunInfo import TaskOperatorOutcome
from core.classes.SubmitApprovedURLTaskOperator import SubmitApprovedURLTaskOperator
from core.enums import RecordType
from helpers.DBDataCreator import BatchURLCreationInfo, DBDataCreator
from pdap_api_client.AccessManager import AccessManager
from pdap_api_client.DTOs import RequestInfo, RequestType, ResponseInfo
from pdap_api_client.PDAPClient import PDAPClient


@pytest.fixture
def mock_pdap_client():
    mock_access_manager = MagicMock(
        spec=AccessManager
    )
    mock_access_manager.make_request = AsyncMock(
        side_effect=[
            ResponseInfo(
                status_code=HTTPStatus.OK,
                data={
                    "id": 21
                }
            ),
            ResponseInfo(
                status_code=HTTPStatus.OK,
                data={
                    "id": 34
                }
            )
        ]
    )
    mock_access_manager.jwt_header = AsyncMock(
        return_value={"Authorization": "Bearer token"}
    )
    pdap_client = PDAPClient(
        access_manager=mock_access_manager
    )
    return pdap_client

async def setup_validated_urls(db_data_creator: DBDataCreator):
    creation_info: BatchURLCreationInfo = await db_data_creator.batch_and_urls(
        url_count=2,
        with_html_content=True
    )
    url_1 = creation_info.url_ids[0]
    url_2 = creation_info.url_ids[1]
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
        user_id=1
    )

@pytest.mark.asyncio
async def test_submit_approved_url_task(
        db_data_creator,
        mock_pdap_client,
        monkeypatch
):
    monkeypatch.setenv("PDAP_API_URL", "http://localhost:8000")

    # Get Task Operator
    operator = SubmitApprovedURLTaskOperator(
        adb_client=db_data_creator.adb_client,
        pdap_client=mock_pdap_client
    )

    # Check Task Operator does not yet meet pre-requisites
    assert not await operator.meets_task_prerequisites()

    # Create URLs with status 'validated' in database and all requisite URL values
    # Ensure they have optional metadata as well
    await setup_validated_urls(db_data_creator)

    # Check Task Operator does meet pre-requisites
    assert await operator.meets_task_prerequisites()

    # Run Task
    run_info = await operator.run_task(task_id=1)

    # Check Task has been marked as completed
    assert run_info.outcome == TaskOperatorOutcome.SUCCESS, run_info.message

    # Get URLs
    urls = await db_data_creator.adb_client.get_all(URL, order_by_attribute="id")
    url_1 = urls[0]
    url_2 = urls[1]

    # Check URLs have been marked as 'submitted'
    assert url_1.outcome == URLStatus.SUBMITTED.value
    assert url_2.outcome == URLStatus.SUBMITTED.value

    # Check URLs now have data source ids
    assert url_1.data_source_id == 21
    assert url_2.data_source_id == 34

    # Check mock method was called twice with expected parameters
    access_manager = mock_pdap_client.access_manager
    assert access_manager.make_request.call_count == 2
    # Check first call


    call_1 = access_manager.make_request.call_args_list[0][0][0]
    expected_call_1 = RequestInfo(
        type_=RequestType.POST,
        url="http://localhost:8000/data-sources",
        headers=access_manager.jwt_header.return_value,
        json={
            "entry_data": {
                "name": "URL 1 Name",
                "source_url": url_1.url,
                "record_type_name": "Accident Reports",
                "description": "URL 1 Description",
                "record_formats": ["Record Format 1", "Record Format 2"],
                "data_portal_type": "Data Portal Type 1",
                "supplying_entity": "Supplying Entity 1"
            },
            "linked_agency_ids": [1, 2]
        }
    )
    assert call_1.type_ == expected_call_1.type_
    assert call_1.url == expected_call_1.url
    assert call_1.headers == expected_call_1.headers
    assert call_1.json == expected_call_1.json
    # Check second call
    call_2 = access_manager.make_request.call_args_list[1][0][0]
    expected_call_2 = RequestInfo(
        type_=RequestType.POST,
        url="http://localhost:8000/data-sources",
        headers=access_manager.jwt_header.return_value,
        json={
            "entry_data": {
                "name": "URL 2 Name",
                "source_url": url_2.url,
                "record_type_name": "Incarceration Records",
                "description": "URL 2 Description",
                "data_portal_type": None,
                "supplying_entity": None,
                "record_formats": None
            },
            "linked_agency_ids": [3, 4]
        }
    )
    assert call_2.type_ == expected_call_2.type_
    assert call_2.url == expected_call_2.url
    assert call_2.headers == expected_call_2.headers
    assert call_2.json == expected_call_2.json