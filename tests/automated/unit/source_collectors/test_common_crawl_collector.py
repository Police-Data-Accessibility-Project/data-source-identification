from unittest import mock

import pytest

from src.collectors.impl.common_crawler.input import CommonCrawlerInputDTO
from src.db.client.async_ import AsyncDatabaseClient
from src.core.logger import AsyncCoreLogger
from src.collectors.impl.common_crawler.collector import CommonCrawlerCollector
from src.db.models.impl.url.core.enums import URLSource
from src.db.models.impl.url.core.pydantic.info import URLInfo


@pytest.fixture
def mock_get_common_crawl_search_results():
    mock_path = "src.collectors.impl.common_crawler.crawler.get_common_crawl_search_results"
    # Results contain other keys, but those are not relevant and thus
    # can be ignored
    mock_results = [
        "http://keyword.com",
        "http://example.com",
        "http://keyword.com/page3"
    ]
    with mock.patch(mock_path) as mock_get_common_crawl_search_results:
        mock_get_common_crawl_search_results.return_value = mock_results
        yield mock_get_common_crawl_search_results

@pytest.mark.asyncio
async def test_common_crawl_collector(mock_get_common_crawl_search_results):
    collector = CommonCrawlerCollector(
        batch_id=1,
        dto=CommonCrawlerInputDTO(
            search_term="keyword",
        ),
        logger=mock.AsyncMock(spec=AsyncCoreLogger),
        adb_client=mock.AsyncMock(spec=AsyncDatabaseClient),
        raise_error=True
    )
    await collector.run()
    mock_get_common_crawl_search_results.assert_called_once()

    collector.adb_client.insert_urls.assert_called_once_with(
        url_infos=[
            URLInfo(url="http://keyword.com", source=URLSource.COLLECTOR),
            URLInfo(url="http://keyword.com/page3", source=URLSource.COLLECTOR),
        ],
        batch_id=1
    )

