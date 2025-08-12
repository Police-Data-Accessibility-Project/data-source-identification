import pytest

from src.core.tasks.url.operators.root_url.core import URLRootURLTaskOperator
from src.db.models.impl.flag.root_url.sqlalchemy import FlagRootURL
from src.db.models.impl.link.urls_root_url.sqlalchemy import LinkURLRootURL
from src.db.models.impl.url.core.enums import URLSource
from src.db.models.impl.url.core.pydantic.insert import URLInsertModel
from tests.automated.integration.tasks.url.impl.asserts import assert_task_ran_without_error
from tests.automated.integration.tasks.url.impl.root_url.constants import ROOT_URL


@pytest.mark.asyncio
async def test_is_root_url(
    operator: URLRootURLTaskOperator
):
    """
    If a URL is a root URL,
    it should be marked as such and not pulled again
    """
    # Check prerequisites not yet met
    assert not await operator.meets_task_prerequisites()

    # Add URL that is a root URL
    url_insert_model = URLInsertModel(
        url=ROOT_URL,
        source=URLSource.DATA_SOURCES
    )
    url_id = (await operator.adb_client.bulk_insert([url_insert_model], return_ids=True))[0]

    # Check prerequisites are now met
    assert await operator.meets_task_prerequisites()

    # Run task
    run_info = await operator.run_task(1)
    assert_task_ran_without_error(run_info)

    # Check task prerequisites no longer met
    assert not await operator.meets_task_prerequisites()

    # Check for absence of Link
    links: list[LinkURLRootURL] = await operator.adb_client.get_all(LinkURLRootURL)
    assert len(links) == 0

    # Check for presence of Flag
    flags: list[FlagRootURL] = await operator.adb_client.get_all(FlagRootURL)
    assert len(flags) == 1
    assert flags[0].url_id == url_id