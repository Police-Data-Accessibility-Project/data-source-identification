import pytest

from src.db.enums import TaskType
from tests.automated.integration.tasks.url.html.asserts import assert_success_url_has_two_html_content_entries, assert_404_url_has_404_status, assert_task_has_one_url_error, \
    assert_task_type_is_html, assert_task_ran_without_error, assert_url_has_one_compressed_html_content_entry
from tests.automated.integration.tasks.asserts import assert_prereqs_not_met, assert_task_has_expected_run_info
from tests.automated.integration.tasks.url.html.setup import setup_urls, setup_operator
from tests.helpers.data_creator.core import DBDataCreator


@pytest.mark.asyncio
async def test_url_html_task(db_data_creator: DBDataCreator):

    operator = await setup_operator()

    # No URLs were created, the prereqs should not be met
    await assert_prereqs_not_met(operator)

    url_ids = await setup_urls(db_data_creator)
    success_url_id = url_ids[0]
    not_found_url_id = url_ids[1]

    task_id = await db_data_creator.adb_client.initiate_task(task_type=TaskType.HTML)
    run_info = await operator.run_task(task_id)
    assert_task_has_expected_run_info(run_info, url_ids)


    task_info = await db_data_creator.adb_client.get_task_info(
        task_id=operator.task_id
    )

    assert_task_ran_without_error(task_info)
    assert_task_type_is_html(task_info)
    assert_task_has_one_url_error(task_info)

    adb = db_data_creator.adb_client
    await assert_success_url_has_two_html_content_entries(adb, run_info, success_url_id)
    await assert_url_has_one_compressed_html_content_entry(adb, success_url_id)
    await assert_404_url_has_404_status(adb, not_found_url_id)


