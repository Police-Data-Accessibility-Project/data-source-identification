import pytest

from src.core.tasks.url.operators.root_url.core import URLRootURLTaskOperator
from src.db.models.impl.flag.root_url.sqlalchemy import FlagRootURL
from src.db.models.impl.link.urls_root_url.sqlalchemy import LinkURLRootURL
from src.db.models.impl.url.core.enums import URLSource
from src.db.models.impl.url.core.pydantic.insert import URLInsertModel
from src.db.models.impl.url.core.sqlalchemy import URL
from tests.automated.integration.tasks.url.impl.asserts import assert_task_ran_without_error
from tests.automated.integration.tasks.url.impl.root_url.constants import BRANCH_URL, ROOT_URL


@pytest.mark.asyncio
async def test_branch_root_url_not_in_db(
    operator: URLRootURLTaskOperator
):
    """
    If a URL is a branch URL,
    with the root URL not in the database,
    Add the root URL and mark it as such
    and add the link to the root URL for the branch
    """
    # Check prerequisites not yet met
    assert not await operator.meets_task_prerequisites()

    # Add URL that is a branch of a root URL
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

    # Check for presence of root URL with proper source and flag
    urls: list[URL] = await operator.adb_client.get_all(URL)
    root_url = next(url for url in urls if url.url == ROOT_URL)
    assert root_url.source == URLSource.ROOT_URL

    # Check for presence of link for branch URL
    links: list[LinkURLRootURL] = await operator.adb_client.get_all(LinkURLRootURL)
    assert len(links) == 1
    link = next(link for link in links if link.url_id == branch_url_id)
    assert link.root_url_id == root_url.id

    # Check for absence of flag for branch URL
    flags: list[FlagRootURL] = await operator.adb_client.get_all(FlagRootURL)
    assert len(flags) == 1
    flag = next(flag for flag in flags if flag.url_id == root_url.id)
    assert flag