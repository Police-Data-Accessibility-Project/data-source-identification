from src.collectors.enums import URLStatus
from src.db.client.async_ import AsyncDatabaseClient
from src.db.enums import TaskType
from tests.automated.integration.tasks.url.html.mocks.constants import MOCK_HTML_CONTENT


async def assert_success_url_has_two_html_content_entries(
    adb: AsyncDatabaseClient,
    run_info,
    url_id: int
):
    await adb.link_urls_to_task(task_id=run_info.task_id, url_ids=run_info.linked_url_ids)
    hci = await adb.get_html_content_info(url_id=url_id)
    assert len(hci) == 2

async def assert_url_has_one_compressed_html_content_entry(
    adb: AsyncDatabaseClient,
    url_id: int
):
    html = await adb.get_html_for_url(url_id=url_id)
    assert html == MOCK_HTML_CONTENT

async def assert_success_url_has_one_compressed_html_content_entry(
    adb: AsyncDatabaseClient,
    run_info,
    url_id: int
):
    await adb.link_urls_to_task(task_id=run_info.task_id, url_ids=run_info.linked_url_ids)
    hci = await adb.get_html_content_info(url_id=url_id)
    assert len(hci) == 1

async def assert_404_url_has_404_status(
    adb: AsyncDatabaseClient,
    url_id: int
):
    url_info_404 = await adb.get_url_info_by_id(url_id=url_id)
    assert url_info_404.outcome == URLStatus.NOT_FOUND


def assert_task_has_one_url_error(task_info):
    assert len(task_info.url_errors) == 1
    assert task_info.url_errors[0].error == "test error"


def assert_task_type_is_html(task_info):
    assert task_info.task_type == TaskType.HTML


def assert_task_ran_without_error(task_info):
    assert task_info.error_info is None
