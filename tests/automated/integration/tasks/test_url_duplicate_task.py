from http import HTTPStatus
from unittest.mock import MagicMock

import pytest

from db.DTOs.URLMapping import URLMapping
from db.models import URL, URLCheckedForDuplicate
from collector_manager.enums import URLStatus
from core.DTOs.TaskOperatorRunInfo import TaskOperatorOutcome
from core.classes.task_operators.URLDuplicateTaskOperator import URLDuplicateTaskOperator
from tests.helpers.DBDataCreator import DBDataCreator
from tests.helpers.test_batch_creation_parameters import TestBatchCreationParameters, TestURLCreationParameters
from pdap_access_manager import ResponseInfo
from pdap_api_client.PDAPClient import PDAPClient


@pytest.mark.asyncio
async def test_url_duplicate_task(
    db_data_creator: DBDataCreator,
    mock_pdap_client: PDAPClient
):


    operator = URLDuplicateTaskOperator(
        adb_client=db_data_creator.adb_client,
        pdap_client=mock_pdap_client
    )

    assert not await operator.meets_task_prerequisites()
    make_request_mock: MagicMock = mock_pdap_client.access_manager.make_request

    make_request_mock.assert_not_called()

    # Add three URLs to the database, one of which is in error, the other two pending
    creation_info = await db_data_creator.batch_v2(
        parameters=TestBatchCreationParameters(
            urls=[
                TestURLCreationParameters(
                    count=1,
                    status=URLStatus.ERROR
                ),
                TestURLCreationParameters(
                    count=2,
                    status=URLStatus.PENDING
                ),
            ]
        )
    )
    pending_urls: list[URLMapping] = creation_info.url_creation_infos[URLStatus.PENDING].url_mappings
    duplicate_url = pending_urls[0]
    non_duplicate_url = pending_urls[1]
    assert await operator.meets_task_prerequisites()
    make_request_mock.assert_not_called()

    make_request_mock.side_effect = [
        ResponseInfo(
            data={
                "duplicates": [
                    {
                        "original_url": duplicate_url.url,
                        "approval_status": "approved"
                    }
                ],
            },
            status_code=HTTPStatus.OK
        ),
        ResponseInfo(
            data={
                "duplicates": [],
            },
            status_code=HTTPStatus.OK
        ),
    ]
    run_info = await operator.run_task(1)
    assert run_info.outcome == TaskOperatorOutcome.SUCCESS, run_info.message
    assert make_request_mock.call_count == 2

    adb_client = db_data_creator.adb_client
    urls: list[URL] = await adb_client.get_all(URL)
    assert len(urls) == 3
    url_ids = [url.id for url in urls]
    assert duplicate_url.url_id in url_ids
    for url in urls:
        if url.id == duplicate_url.url_id:
            assert url.outcome == URLStatus.DUPLICATE.value

    checked_for_duplicates: list[URLCheckedForDuplicate] = await adb_client.get_all(URLCheckedForDuplicate)
    assert len(checked_for_duplicates) == 2
    checked_for_duplicate_url_ids = [url.url_id for url in checked_for_duplicates]
    assert duplicate_url.url_id in checked_for_duplicate_url_ids
    assert non_duplicate_url.url_id in checked_for_duplicate_url_ids

    assert not await operator.meets_task_prerequisites()





