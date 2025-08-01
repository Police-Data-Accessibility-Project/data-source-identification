import pytest

from src.core.enums import BatchStatus
from src.db.models.instantiations.batch.pydantic import BatchInfo
from src.db.models.instantiations.link.batch_url import LinkBatchURL
from src.db.models.instantiations.url.core.pydantic.info import URLInfo
from src.db.models.instantiations.url.core.sqlalchemy import URL


@pytest.mark.asyncio
async def test_insert_urls(
        db_client_test,
        adb_client_test
):
    # Insert batch
    batch_info = BatchInfo(
        strategy="ckan",
        status=BatchStatus.IN_PROCESS,
        parameters={},
        user_id=1
    )
    batch_id = await adb_client_test.insert_batch(batch_info)

    urls = [
        URLInfo(
            url="https://example.com/1",
            collector_metadata={"name": "example_1"},
        ),
        URLInfo(
            url="https://example.com/2",
        ),
        # Duplicate
        URLInfo(
            url="https://example.com/1",
            collector_metadata={"name": "example_duplicate"},
        )
    ]
    insert_urls_info = await adb_client_test.insert_urls(
        url_infos=urls,
        batch_id=batch_id
    )

    url_mappings = insert_urls_info.url_mappings
    assert len(url_mappings) == 2
    assert url_mappings[0].url == "https://example.com/1"
    assert url_mappings[1].url == "https://example.com/2"


    assert insert_urls_info.original_count == 2
    assert insert_urls_info.duplicate_count == 1

    urls = await adb_client_test.get_all(URL)
    assert len(urls) == 2

    links: list[LinkBatchURL] = await adb_client_test.get_all(LinkBatchURL)
    assert len(links) == 2
    for link in links:
        assert link.batch_id == batch_id
