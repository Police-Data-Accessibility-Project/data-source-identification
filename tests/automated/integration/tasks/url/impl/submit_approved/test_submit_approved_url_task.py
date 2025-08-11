import pytest
from deepdiff import DeepDiff

from src.core.tasks.url.operators.submit_approved.core import SubmitApprovedURLTaskOperator
from src.db.enums import TaskType
from src.db.models.instantiations.url.error_info.sqlalchemy import URLErrorInfo
from src.db.models.instantiations.url.data_source.sqlalchemy import URLDataSource
from src.db.models.instantiations.url.core.sqlalchemy import URL
from src.collectors.enums import URLStatus
from src.core.tasks.url.enums import TaskOperatorOutcome
from tests.automated.integration.tasks.url.impl.submit_approved.mock import mock_make_request
from tests.automated.integration.tasks.url.impl.submit_approved.setup import setup_validated_urls
from pdap_access_manager import RequestInfo, RequestType, DataSourcesNamespaces
from src.external.pdap.client import PDAPClient


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
    assert url_1.status == URLStatus.SUBMITTED
    assert url_2.status == URLStatus.SUBMITTED
    assert url_3.status == URLStatus.ERROR

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
    access_manager.build_url.assert_called_with(
        namespace=DataSourcesNamespaces.SOURCE_COLLECTOR,
        subdomains=['data-sources']
    )

    call_1 = access_manager.make_request.call_args_list[0][0][0]
    expected_call_1 = RequestInfo(
        type_=RequestType.POST,
        url="http://example.com",
        headers=access_manager.jwt_header.return_value,
        json_={
            "data_sources": [
                {
                    "name": "URL 1 Name",
                    "source_url": url_1.url,
                    "record_type": "Accident Reports",
                    "description": None,
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
    assert call_1.headers == expected_call_1.headers
    diff = DeepDiff(call_1.json_, expected_call_1.json_, ignore_order=True)
    assert diff == {}, f"Differences found: {diff}"
