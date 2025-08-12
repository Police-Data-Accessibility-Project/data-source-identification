from unittest.mock import AsyncMock

import pytest

from src.collectors.impl.auto_googler.dtos.query_results import GoogleSearchQueryResultsInnerDTO
from src.collectors.impl.auto_googler.dtos.input import AutoGooglerInputDTO
from src.db.client.async_ import AsyncDatabaseClient
from src.core.logger import AsyncCoreLogger
from src.collectors.impl.auto_googler.collector import AutoGooglerCollector
from src.db.models.impl.url.core.enums import URLSource
from src.db.models.impl.url.core.pydantic.info import URLInfo


@pytest.fixture
def patch_get_query_results(monkeypatch):
    patch_path = "src.collectors.impl.auto_googler.searcher.GoogleSearcher.get_query_results"
    mock = AsyncMock()
    mock.side_effect = [
        [GoogleSearchQueryResultsInnerDTO(url="https://include.com/1", title="keyword", snippet="snippet 1"),],
        None
    ]
    monkeypatch.setattr(patch_path, mock)
    yield mock

@pytest.mark.asyncio
async def test_auto_googler_collector(patch_get_query_results):
    mock = patch_get_query_results
    collector = AutoGooglerCollector(
        batch_id=1,
        dto=AutoGooglerInputDTO(
            queries=["keyword"]
        ),
        logger=AsyncMock(spec=AsyncCoreLogger),
        adb_client=AsyncMock(spec=AsyncDatabaseClient),
        raise_error=True
    )
    await collector.run()
    mock.assert_called_once_with("keyword")

    collector.adb_client.insert_urls.assert_called_once_with(
        url_infos=[
            URLInfo(
                url="https://include.com/1",
                collector_metadata={"query": "keyword", "title": "keyword", "snippet": "snippet 1"},
                source=URLSource.COLLECTOR
            )
        ],
        batch_id=1
    )