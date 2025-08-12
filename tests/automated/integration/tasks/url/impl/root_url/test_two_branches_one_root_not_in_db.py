import pytest

from src.core.tasks.url.operators.root_url.core import URLRootURLTaskOperator
from src.db.models.impl.url.core.enums import URLSource
from src.db.models.impl.url.core.pydantic.insert import URLInsertModel
from tests.automated.integration.tasks.url.impl.asserts import assert_task_ran_without_error
from tests.automated.integration.tasks.url.impl.root_url.constants import BRANCH_URL, SECOND_BRANCH_URL


@pytest.mark.asyncio
@pytest.mark.asyncio
async def test_two_branches_one_root_in_db_not_flagged(
    operator: URLRootURLTaskOperator
):
    """
    If two URLs are branches of a ROOT URL that is not already in the database,
    Both URLs, along with the Root URL, should be added to the database
    and the Root URL should flagged as such
    """
    # Check prerequisites not yet met
    assert not await operator.meets_task_prerequisites()

    # Add two URLs that are branches of a root URL
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

