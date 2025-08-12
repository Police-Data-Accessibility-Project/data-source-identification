import pytest

from src.core.tasks.url.operators.root_url.core import URLRootURLTaskOperator
from src.db.models.impl.flag.root_url.pydantic import FlagRootURLPydantic
from src.db.models.impl.link.urls_root_url.sqlalchemy import LinkURLRootURL
from src.db.models.impl.url.core.enums import URLSource
from src.db.models.impl.url.core.pydantic.insert import URLInsertModel
from tests.automated.integration.tasks.url.impl.asserts import assert_task_ran_without_error
from tests.automated.integration.tasks.url.impl.root_url.constants import ROOT_URL, BRANCH_URL, SECOND_BRANCH_URL


@pytest.mark.asyncio
async def test_two_branches_one_root_in_db(
    operator: URLRootURLTaskOperator
):
    """
    If two URLs are branches of a ROOT URL that is already in the database,
    Both URLs should be linked to the ROOT URL
    """
    # Check prerequisites not yet met
    assert not await operator.meets_task_prerequisites()

    # Add root URL and mark as such
    url_insert_model_root = URLInsertModel(
        url=ROOT_URL,
        source=URLSource.DATA_SOURCES
    )
    url_id_root = (await operator.adb_client.bulk_insert([url_insert_model_root], return_ids=True))[0]
    root_model_flag_insert = FlagRootURLPydantic(
        url_id=url_id_root
    )
    await operator.adb_client.bulk_insert([root_model_flag_insert])

    # Add two URLs that are branches of that root URL
    url_insert_model_branch_1 = URLInsertModel(
        url=BRANCH_URL,
        source=URLSource.COLLECTOR
    )
    url_id_branch_1 = (await operator.adb_client.bulk_insert([url_insert_model_branch_1], return_ids=True))[0]

    url_insert_model_branch_2 = URLInsertModel(
        url=SECOND_BRANCH_URL,
        source=URLSource.COLLECTOR
    )
    url_id_branch_2 = (await operator.adb_client.bulk_insert([url_insert_model_branch_2], return_ids=True))[0]

    # Check prerequisites are now met
    assert await operator.meets_task_prerequisites()

    # Run task
    run_info = await operator.run_task(1)
    assert_task_ran_without_error(run_info)

    # Check task prerequisites no longer met
    assert not await operator.meets_task_prerequisites()

    # Check for presence of separate links for both branch URLs
    links: list[LinkURLRootURL] = await operator.adb_client.get_all(LinkURLRootURL)
    assert len(links) == 2
    link_url_ids = {link.url_id for link in links}
    assert link_url_ids == {url_id_branch_1, url_id_branch_2}
