import pytest

from src.db.client.async_ import AsyncDatabaseClient
from src.db.enums import TaskType
from tests.automated.integration.tasks.url.impl.asserts import assert_prereqs_not_met, assert_prereqs_met, \
    assert_task_ran_without_error
from tests.automated.integration.tasks.url.impl.html.check.manager import TestURLHTMLTaskCheckManager
from tests.automated.integration.tasks.url.impl.html.setup.manager import setup_operator, \
    TestURLHTMLTaskSetupManager


@pytest.mark.asyncio
async def test_url_html_task(adb_client_test: AsyncDatabaseClient):
    setup = TestURLHTMLTaskSetupManager(adb_client_test)

    operator = await setup_operator()

    # No URLs were created, the prereqs should not be met
    await assert_prereqs_not_met(operator)

    records = await setup.setup()
    await assert_prereqs_met(operator)

    task_id = await adb_client_test.initiate_task(task_type=TaskType.HTML)
    run_info = await operator.run_task(task_id)
    assert_task_ran_without_error(run_info)

    checker = TestURLHTMLTaskCheckManager(
        adb_client=adb_client_test,
        records=records
    )
    await checker.check()

    await assert_prereqs_not_met(operator)
