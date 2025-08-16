import pytest

from src.core.tasks.dtos.run_info import URLTaskOperatorRunInfo
from src.core.tasks.url.operators.internet_archives.core import URLInternetArchivesTaskOperator
from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.impl.flag.checked_for_ia.sqlalchemy import FlagURLCheckedForInternetArchives
from src.db.models.impl.url.ia_metadata.sqlalchemy import URLInternetArchivesMetadata
from src.external.internet_archives.models.capture import IACapture
from tests.automated.integration.tasks.url.impl.asserts import assert_task_ran_without_error
from tests.automated.integration.tasks.url.impl.ia_metadata.constants import TEST_URL_1, TEST_URL_2
from tests.automated.integration.tasks.url.impl.ia_metadata.setup import add_urls


@pytest.mark.asyncio
async def test_happy_path(operator: URLInternetArchivesTaskOperator) -> None:
    """
    If URLs are present in the database and have not been processed yet,
    They should be processed, and flagged as checked for
    If the client returns a valid response,
    the internet archive metadata should be added
    """
    adb_client: AsyncDatabaseClient = operator.adb_client

    # Confirm operator does not yet meet prerequisites
    assert not await operator.meets_task_prerequisites()

    # Add URLs to database
    url_ids: list[int] = await add_urls(adb_client)

    # Confirm operator now meets prerequisites
    assert await operator.meets_task_prerequisites()

    # Set IA Client to return valid response
    operator.ia_client._get_url_snapshot.side_effect = [
        IACapture(
            timestamp=1045890000,
            original=TEST_URL_1,
            length=1000,
            digest="a4kf189"
        ),
        IACapture(
            timestamp=1045890001,
            original=TEST_URL_2,
            length=2000,
            digest="g19f189"
        )
    ]

    # Run task
    run_info: URLTaskOperatorRunInfo = await operator.run_task(1)

    # Confirm task ran without error
    assert_task_ran_without_error(run_info)

    # Confirm operator no longer meets prerequisites
    assert not await operator.meets_task_prerequisites()

    # Confirm URLs have been marked as checked, with success = True
    flags: list[FlagURLCheckedForInternetArchives] = await adb_client.get_all(FlagURLCheckedForInternetArchives)
    assert len(flags) == 2
    assert {flag.url_id for flag in flags} == set(url_ids)
    assert all(flag.success for flag in flags)

    # Confirm IA metadata has been added
    metadata_list: list[URLInternetArchivesMetadata] = await adb_client.get_all(URLInternetArchivesMetadata)
    assert len(metadata_list) == 2
    assert {metadata.url_id for metadata in metadata_list} == set(url_ids)
    assert {metadata.archive_url for metadata in metadata_list} == {
        f"https://web.archive.org/web/1045890000/{TEST_URL_1}",
        f"https://web.archive.org/web/1045890001/{TEST_URL_2}"
    }
    assert {metadata.digest for metadata in metadata_list} == {"a4kf189", "g19f189"}
    assert {metadata.length for metadata in metadata_list} == {1000, 2000}