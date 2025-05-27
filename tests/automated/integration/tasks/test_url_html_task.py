import types
from http import HTTPStatus
from typing import Optional

import pytest
from aiohttp import ClientResponseError, RequestInfo

from src.db.AsyncDatabaseClient import AsyncDatabaseClient
from src.db.enums import TaskType
from src.collector_manager.enums import URLStatus
from src.core.DTOs.TaskOperatorRunInfo import TaskOperatorOutcome
from src.core.classes.task_operators.URLHTMLTaskOperator import URLHTMLTaskOperator
from src.html_tag_collector.DataClassTags import ResponseHTMLInfo
from tests.helpers.DBDataCreator import DBDataCreator
from src.html_tag_collector.ResponseParser import HTMLResponseParser
from src.html_tag_collector.RootURLCache import RootURLCache
from src.html_tag_collector.URLRequestInterface import URLRequestInterface, URLResponseInfo


@pytest.mark.asyncio
async def test_url_html_task(db_data_creator: DBDataCreator):

    mock_html_content = "<html></html>"
    mock_content_type = "text/html"

    async def mock_make_requests(self, urls: list[str]) -> list[URLResponseInfo]:
        results = []
        for idx, url in enumerate(urls):
            if idx == 1:
                results.append(
                    URLResponseInfo(
                        success=False,
                        content_type=mock_content_type,
                        exception=str(ClientResponseError(
                            request_info=RequestInfo(
                                url=url,
                                method="GET",
                                real_url=url,
                                headers={},
                            ),
                            code=HTTPStatus.NOT_FOUND.value,
                            history=(None,),
                        )),
                        status=HTTPStatus.NOT_FOUND
                    )
                )
                continue

            if idx == 2:
                results.append(
                    URLResponseInfo(
                        success=False,
                        exception=str(ValueError("test error")),
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
    url_request_interface.make_requests_with_html = types.MethodType(mock_make_requests, url_request_interface)

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

    meets_prereqs = await operator.meets_task_prerequisites()
    # Check that, because no URLs were created, the prereqs are not met
    assert not meets_prereqs

    batch_id = db_data_creator.batch()
    url_mappings = db_data_creator.urls(batch_id=batch_id, url_count=3).url_mappings
    url_ids = [url_info.url_id for url_info in url_mappings]

    task_id = await db_data_creator.adb_client.initiate_task(task_type=TaskType.HTML)
    run_info = await operator.run_task(task_id)
    assert run_info.outcome == TaskOperatorOutcome.SUCCESS
    assert run_info.linked_url_ids == url_ids


    # Check in database that
    # - task type is listed as 'HTML'
    # - task has 3 urls
    # - task has one errored url with error "ValueError"
    task_info = await db_data_creator.adb_client.get_task_info(
        task_id=operator.task_id
    )

    assert task_info.error_info is None
    assert task_info.task_type == TaskType.HTML

    assert len(task_info.url_errors) == 1
    assert task_info.url_errors[0].error == "test error"

    adb = db_data_creator.adb_client
    # Check that success url has two rows of HTML data
    await adb.link_urls_to_task(task_id=run_info.task_id, url_ids=run_info.linked_url_ids)
    hci = await adb.get_html_content_info(url_id=url_ids[0])
    assert len(hci) == 2

    # Check that 404 url has status of 404
    url_info_404 = await adb.get_url_info_by_id(url_id=url_ids[1])
    assert url_info_404.outcome == URLStatus.NOT_FOUND
    # Check that errored url has error info
