import types
from typing import Optional

import pytest

from collector_db.AsyncDatabaseClient import AsyncDatabaseClient
from collector_db.enums import TaskType
from collector_db.models import Task
from core.classes.URLHTMLTaskOperator import URLHTMLTaskOperator
from core.enums import BatchStatus
from helpers.DBDataCreator import DBDataCreator
from helpers.assert_functions import assert_database_has_no_tasks
from html_tag_collector.DataClassTags import ResponseHTMLInfo
from html_tag_collector.ResponseParser import HTMLResponseParser
from html_tag_collector.RootURLCache import RootURLCache
from html_tag_collector.URLRequestInterface import URLRequestInterface, URLResponseInfo


@pytest.mark.asyncio
async def test_url_html_task(db_data_creator: DBDataCreator):

    mock_html_content = "<html></html>"
    mock_content_type = "text/html"

    async def mock_make_requests(self, urls: list[str]) -> list[URLResponseInfo]:
        results = []
        for idx, url in enumerate(urls):
            if idx == 2:
                results.append(
                    URLResponseInfo(
                        success=False,
                        exception=ValueError("test error"),
                        content_type=mock_content_type
                    ))
            else:
                results.append(URLResponseInfo(
                    html=mock_html_content, success=True, content_type=mock_content_type))
        return results

    async def mock_parse(self, url: str, html_content: str, content_type: str) -> ResponseHTMLInfo:
        assert html_content == mock_html_content
        assert content_type == mock_content_type
        return ResponseHTMLInfo(
            url=url,
            title="fake title",
            description="fake description",
        )

    async def mock_get_from_cache(self, url: str) -> Optional[str]:
        return None

    # Add mock methods or mock classes
    url_request_interface = URLRequestInterface()
    url_request_interface.make_requests = types.MethodType(mock_make_requests, url_request_interface)

    mock_root_url_cache = RootURLCache()
    mock_root_url_cache.get_from_cache = types.MethodType(mock_get_from_cache, mock_root_url_cache)

    html_parser = HTMLResponseParser(
        root_url_cache=mock_root_url_cache
    )
    html_parser.parse = types.MethodType(mock_parse, html_parser)

    operator = URLHTMLTaskOperator(
        adb_client=AsyncDatabaseClient(),
        url_request_interface=url_request_interface,
        html_parser=html_parser
    )
    await operator.run_task()

    # Check that, because no URLs were created, the task did not run
    await assert_database_has_no_tasks(db_data_creator.adb_client)

    batch_id = db_data_creator.batch()
    url_mappings = db_data_creator.urls(batch_id=batch_id, url_count=3).url_mappings
    url_ids = [url_info.url_id for url_info in url_mappings]

    await operator.run_task()


    # Check in database that
    # - task is listed as complete
    # - task type is listed as 'HTML'
    # - task has 3 urls
    # - task has one errored url with error "ValueError"
    task_info = await db_data_creator.adb_client.get_task_info(
        task_id=operator.task_id
    )

    assert task_info.error_info is None
    assert task_info.task_status == BatchStatus.COMPLETE
    assert task_info.task_type == TaskType.HTML

    assert len(task_info.urls) == 3
    assert len(task_info.url_errors) == 1
    assert task_info.url_errors[0].error == "test error"

    adb = db_data_creator.adb_client
    # Check that both success urls have two rows of HTML data
    hci = await adb.get_html_content_info(url_id=task_info.urls[0].id)
    assert len(hci) == 2
    hci = await adb.get_html_content_info(url_id=task_info.urls[1].id)
    assert len(hci) == 2

    # Check that errored url has error info
