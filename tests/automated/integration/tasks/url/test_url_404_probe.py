import types
from http import HTTPStatus

import pendulum
import pytest
from aiohttp import ClientResponseError, RequestInfo

from src.core.tasks.url.operators.probe_404.core import URL404ProbeTaskOperator
from src.external.url_request.core import URLRequestInterface
from src.db.models.instantiations.url.probed_for_404 import URLProbedFor404
from src.db.models.instantiations.url.core.sqlalchemy import URL
from src.collectors.enums import URLStatus
from src.core.tasks.url.enums import TaskOperatorOutcome
from src.external.url_request.dtos.url_response import URLResponseInfo
from tests.helpers.data_creator.core import DBDataCreator
from tests.helpers.batch_creation_parameters.url_creation_parameters import TestURLCreationParameters
from tests.helpers.batch_creation_parameters.core import TestBatchCreationParameters


@pytest.mark.asyncio
async def test_url_404_probe_task(db_data_creator: DBDataCreator):

    mock_html_content = "<html></html>"
    mock_content_type = "text/html"
    adb_client = db_data_creator.adb_client

    async def mock_make_simple_requests(self, urls: list[str]) -> list[URLResponseInfo]:
        """
        Mock make_simple_requests so that
        - the first url returns a 200
        - the second url returns a 404
        - the third url returns a general error

        """
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
            elif idx == 2:
                results.append(
                    URLResponseInfo(
                        success=False,
                        exception=str(ValueError("test error")),
                        content_type=mock_content_type
                    )
                )
            else:
                results.append(URLResponseInfo(
                    html=mock_html_content, success=True, content_type=mock_content_type))
        return results

    url_request_interface = URLRequestInterface()
    url_request_interface.make_simple_requests = types.MethodType(mock_make_simple_requests, url_request_interface)

    operator = URL404ProbeTaskOperator(
        url_request_interface=url_request_interface,
        adb_client=adb_client
    )
    # Check that initially prerequisites aren't met
    meets_prereqs = await operator.meets_task_prerequisites()
    assert not meets_prereqs

    # Add 4 URLs, 3 pending, 1 error
    creation_info = await db_data_creator.batch_v2(
        parameters=TestBatchCreationParameters(
            urls=[
                TestURLCreationParameters(
                    count=3,
                    status=URLStatus.PENDING,
                    with_html_content=True
                ),
                TestURLCreationParameters(
                    count=1,
                    status=URLStatus.ERROR,
                    with_html_content=False
                ),
            ]
        )
    )

    meets_prereqs = await operator.meets_task_prerequisites()
    assert meets_prereqs

    # Run task and validate results
    run_info = await operator.run_task(task_id=1)
    assert run_info.outcome == TaskOperatorOutcome.SUCCESS, run_info.message


    pending_url_mappings = creation_info.urls_by_status[URLStatus.PENDING].url_mappings
    url_id_success = pending_url_mappings[0].url_id
    url_id_404 = pending_url_mappings[1].url_id
    url_id_error = pending_url_mappings[2].url_id

    url_id_initial_error = creation_info.urls_by_status[URLStatus.ERROR].url_mappings[0].url_id

    # Check that URLProbedFor404 has been appropriately populated
    probed_for_404_objects: list[URLProbedFor404] = await db_data_creator.adb_client.get_all(URLProbedFor404)

    assert len(probed_for_404_objects) == 3
    assert probed_for_404_objects[0].url_id == url_id_success
    assert probed_for_404_objects[1].url_id == url_id_404
    assert probed_for_404_objects[2].url_id == url_id_error

    # Check that the URLs have been updated appropriated
    urls: list[URL] = await adb_client.get_all(URL)

    def find_url(url_id: int) -> URL:
        for url in urls:
            if url.id == url_id:
                return url
        raise Exception(f"URL with id {url_id} not found")

    assert find_url(url_id_success).outcome == URLStatus.PENDING
    assert find_url(url_id_404).outcome == URLStatus.NOT_FOUND
    assert find_url(url_id_error).outcome == URLStatus.PENDING
    assert find_url(url_id_initial_error).outcome == URLStatus.ERROR

    # Check that meets_task_prerequisites now returns False
    meets_prereqs = await operator.meets_task_prerequisites()
    assert not meets_prereqs

    # Check that meets_task_prerequisites returns True
    # After setting the last probed for 404 date to 2 months ago
    two_months_ago = pendulum.now().subtract(months=2).naive()
    await adb_client.mark_all_as_recently_probed_for_404(
        [url_id_404, url_id_error],
        dt=two_months_ago
    )

    meets_prereqs = await operator.meets_task_prerequisites()
    assert meets_prereqs

    # Run the task and Ensure all but the URL previously marked as 404 have been checked again
    run_info = await operator.run_task(task_id=2)
    assert run_info.outcome == TaskOperatorOutcome.SUCCESS, run_info.message

    probed_for_404_objects: list[URLProbedFor404] = await db_data_creator.adb_client.get_all(URLProbedFor404)

    assert len(probed_for_404_objects) == 3
    assert probed_for_404_objects[0].last_probed_at != two_months_ago
    assert probed_for_404_objects[1].last_probed_at == two_months_ago
    assert probed_for_404_objects[2].last_probed_at != two_months_ago






