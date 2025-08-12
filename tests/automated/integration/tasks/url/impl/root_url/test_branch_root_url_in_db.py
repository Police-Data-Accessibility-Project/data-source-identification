import pytest

from src.core.tasks.url.operators.root_url.core import URLRootURLTaskOperator
from src.db.models.impl.flag.root_url.pydantic import FlagRootURLPydantic
from src.db.models.impl.flag.root_url.sqlalchemy import FlagRootURL
from src.db.models.impl.link.urls_root_url.sqlalchemy import LinkURLRootURL
from src.db.models.impl.url.core.enums import URLSource
from src.db.models.impl.url.core.pydantic.insert import URLInsertModel
from tests.automated.integration.tasks.url.impl.asserts import assert_task_ran_without_error
from tests.automated.integration.tasks.url.impl.root_url.constants import ROOT_URL, BRANCH_URL


@pytest.mark.asyncio
async def test_branch_root_url_in_db(
    operator: URLRootURLTaskOperator
):
    """
    If a URL is a branch URL,
    with the root URL in the database,
    it should be marked as such and not pulled again
    """
    # Check prerequisites not yet met
    assert not await operator.meets_task_prerequisites()

    # Add URL that is a root URL, and mark as such
    url_insert_model_root = URLInsertModel(
        url=ROOT_URL,
        source=URLSource.DATA_SOURCES
    )
    root_url_id = (await operator.adb_client.bulk_insert([url_insert_model_root], return_ids=True))[0]
    root_model_flag_insert = FlagRootURLPydantic(
        url_id=root_url_id
    )
    await operator.adb_client.bulk_insert([root_model_flag_insert])

    # Add URL that is a branch of the root URL
    url_insert_model = URLInsertModel(
        url=BRANCH_URL,
        source=URLSource.COLLECTOR
    )
    branch_url_id = (await operator.adb_client.bulk_insert([url_insert_model], return_ids=True))[0]

    # Check prerequisites are now met
    assert await operator.meets_task_prerequisites()

    # Run task
    run_info = await operator.run_task(1)
    assert_task_ran_without_error(run_info)

    # Check task prerequisites no longer met
    assert not await operator.meets_task_prerequisites()

    links: list[LinkURLRootURL] = await operator.adb_client.get_all(LinkURLRootURL)
    assert len(links) == 1
    assert links[0].url_id == branch_url_id

    # Check for only one flag, for the root URL
    flags: list[FlagRootURL] = await operator.adb_client.get_all(FlagRootURL)
    assert len(flags) == 1
    assert flags[0].url_id == root_url_id