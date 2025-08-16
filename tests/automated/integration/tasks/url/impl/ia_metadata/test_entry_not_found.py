import pytest

from src.core.tasks.url.operators.internet_archives.core import URLInternetArchivesTaskOperator
from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.impl.flag.checked_for_ia.sqlalchemy import FlagURLCheckedForInternetArchives
from src.db.models.impl.url.ia_metadata.sqlalchemy import URLInternetArchivesMetadata
from tests.automated.integration.tasks.url.impl.asserts import assert_task_ran_without_error
from tests.automated.integration.tasks.url.impl.ia_metadata.setup import add_urls


@pytest.mark.asyncio
async def test_entry_not_found(operator: URLInternetArchivesTaskOperator) -> None:
    """
    If URLs are present in the database and have not been processed yet,
    They should be processed, and flagged as checked for
    If the client finds no archive metadata for the URL,
    the internet archive metadata should not be added
    """
    adb_client: AsyncDatabaseClient = operator.adb_client

    # Confirm operator does not yet meet prerequisites
    assert not await operator.meets_task_prerequisites()

    # Add URLs to database
    url_ids: list[int] = await add_urls(adb_client)

    # Confirm operator now meets prerequisites
    assert await operator.meets_task_prerequisites()

    # Set IA Client to return None
    operator.ia_client._get_url_snapshot.side_effect = [
        None,
        None
    ]

    # Run task
    run_info = await operator.run_task(1)

    # Confirm task ran without error
    assert_task_ran_without_error(run_info)

    # Confirm operator no longer meets prerequisites
    assert not await operator.meets_task_prerequisites()

    # Confirm URLs have been marked as checked, with success = True
    flags: list[FlagURLCheckedForInternetArchives] = await adb_client.get_all(FlagURLCheckedForInternetArchives)
    assert len(flags) == 2
    assert {flag.url_id for flag in flags} == set(url_ids)
    assert all(flag.success for flag in flags)


    # Confirm IA metadata has not been added
    metadata_list: list[URLInternetArchivesMetadata] = await adb_client.get_all(URLInternetArchivesMetadata)
    assert len(metadata_list) == 0
