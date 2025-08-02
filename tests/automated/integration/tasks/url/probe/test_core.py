import pytest

from src.core.tasks.url.operators.probe.core import URLProbeTaskOperator
from tests.automated.integration.tasks.asserts import assert_task_ran_without_error
from tests.automated.integration.tasks.url.probe.setup.core import create_urls_in_db
from tests.automated.integration.tasks.url.probe.setup.queries.check import CheckURLsInDBForURLProbeTaskQueryBuilder


@pytest.mark.asyncio
async def test_url_probe_task(
    operator: URLProbeTaskOperator
):
    adb_client = operator.adb_client
    # Check task does not yet meet pre-requisites
    assert not await operator.meets_task_prerequisites()

    # Set up URLs
    await create_urls_in_db(adb_client=adb_client)

    # Check task meets pre-requisites
    assert await operator.meets_task_prerequisites()

    # Run task
    run_info = await operator.run_task(1)
    assert_task_ran_without_error(run_info)

    # Check task no longer meets pre-requisites
    assert not await operator.meets_task_prerequisites()

    # Check results as expected
    await adb_client.run_query_builder(
        CheckURLsInDBForURLProbeTaskQueryBuilder()
    )
