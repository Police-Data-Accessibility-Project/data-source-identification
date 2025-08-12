from unittest import mock
from unittest.mock import MagicMock, call, AsyncMock

import pytest

from src.collectors.impl.muckrock.collectors.county.core import MuckrockCountyLevelSearchCollector
from src.collectors.impl.muckrock.collectors.simple.core import MuckrockSimpleSearchCollector
from src.db.client.async_ import AsyncDatabaseClient
from src.core.logger import AsyncCoreLogger
from src.collectors.impl.muckrock.collectors.county.dto import MuckrockCountySearchCollectorInputDTO
from src.collectors.impl.muckrock.collectors.simple.dto import MuckrockSimpleSearchCollectorInputDTO
from src.collectors.impl.muckrock.fetch_requests.foia import FOIAFetchRequest
from src.db.models.impl.url.core.enums import URLSource
from src.db.models.impl.url.core.pydantic.info import URLInfo

PATCH_ROOT = "src.collectors.impl.muckrock"

@pytest.fixture
def patch_muckrock_fetcher(monkeypatch):
    patch_path = f"{PATCH_ROOT}.fetchers.templates.fetcher.MuckrockFetcherBase.fetch"
    inner_test_data = [
        {"absolute_url": "https://include.com/1", "title": "keyword"},
        {"absolute_url": "https://include.com/2", "title": "keyword"},
        {"absolute_url": "https://exclude.com/3", "title": "lemon"},
    ]
    test_data = {
        "results": inner_test_data
    }
    mock = AsyncMock()

    mock.return_value = test_data
    monkeypatch.setattr(patch_path, mock)
    return mock


@pytest.mark.asyncio
async def test_muckrock_simple_collector(patch_muckrock_fetcher):
    collector = MuckrockSimpleSearchCollector(
        batch_id=1,
        dto=MuckrockSimpleSearchCollectorInputDTO(
            search_string="keyword",
            max_results=2
        ),
        logger=mock.AsyncMock(spec=AsyncCoreLogger),
        adb_client=mock.AsyncMock(spec=AsyncDatabaseClient),
        raise_error=True
    )
    await collector.run()
    patch_muckrock_fetcher.assert_has_calls(
        [
            call(FOIAFetchRequest(page=1, page_size=100)),
        ]
    )
    collector.adb_client.insert_urls.assert_called_once_with(
        url_infos=[
            URLInfo(
                url='https://include.com/1',
                collector_metadata={'absolute_url': 'https://include.com/1', 'title': 'keyword'},
                source=URLSource.COLLECTOR
            ),
            URLInfo(
                url='https://include.com/2',
                collector_metadata={'absolute_url': 'https://include.com/2', 'title': 'keyword'},
                source=URLSource.COLLECTOR
            )
        ],
        batch_id=1
    )


@pytest.fixture
def patch_muckrock_county_level_search_collector_methods(monkeypatch):
    patch_root = (f"{PATCH_ROOT}.collectors.county.core."
                  "MuckrockCountyLevelSearchCollector.")
    patch_path_get_jurisdiction_ids = patch_root + "get_jurisdiction_ids"
    patch_path_get_foia_records = patch_root + "get_foia_records"
    get_jurisdiction_ids_data = {
        "Alpha": 1,
        "Beta": 2
    }
    get_foia_records_data = [
        {"absolute_url": "https://include.com/1", "title": "keyword"},
        {"absolute_url": "https://include.com/2", "title": "keyword"},
        {"absolute_url": "https://include.com/3", "title": "lemon"},
    ]
    mock = MagicMock()
    mock.get_jurisdiction_ids = AsyncMock(return_value=get_jurisdiction_ids_data)
    mock.get_foia_records = AsyncMock(return_value=get_foia_records_data)
    monkeypatch.setattr(patch_path_get_jurisdiction_ids, mock.get_jurisdiction_ids)
    monkeypatch.setattr(patch_path_get_foia_records, mock.get_foia_records)
    return mock

@pytest.mark.asyncio
async def test_muckrock_county_search_collector(patch_muckrock_county_level_search_collector_methods):
    mock_methods = patch_muckrock_county_level_search_collector_methods

    collector = MuckrockCountyLevelSearchCollector(
        batch_id=1,
        dto=MuckrockCountySearchCollectorInputDTO(
            parent_jurisdiction_id=1,
            town_names=["test"]
        ),
        logger=AsyncMock(spec=AsyncCoreLogger),
        adb_client=AsyncMock(spec=AsyncDatabaseClient),
        raise_error=True
    )
    await collector.run()

    mock_methods.get_jurisdiction_ids.assert_called_once()
    mock_methods.get_foia_records.assert_called_once_with({"Alpha": 1, "Beta": 2})

    collector.adb_client.insert_urls.assert_called_once_with(
        url_infos=[
            URLInfo(
                url='https://include.com/1',
                collector_metadata={'absolute_url': 'https://include.com/1', 'title': 'keyword'},
                source=URLSource.COLLECTOR
            ),
            URLInfo(
                url='https://include.com/2',
                collector_metadata={'absolute_url': 'https://include.com/2', 'title': 'keyword'},
                source=URLSource.COLLECTOR
            ),
            URLInfo(
                url='https://include.com/3',
                collector_metadata={'absolute_url': 'https://include.com/3', 'title': 'lemon'},
                source=URLSource.COLLECTOR
            ),
        ],
        batch_id=1
    )


@pytest.fixture
def patch_muckrock_full_search_collector(monkeypatch):
    module_path = f"{PATCH_ROOT}.collectors.all_foia.core.MuckrockAllFOIARequestsCollector"
    patch_path = f"{module_path}.get_page_data"
    test_data = [{
        "results": [
            {
                "absolute_url": "https://include.com/1",
                "title": "keyword"
            },
            {
                "absolute_url": "https://include.com/2",
                "title": "keyword"
            },
            {
                "absolute_url": "https://include.com/3",
                "title": "lemon"
            }
        ]
    }]
    mock = AsyncMock()
    mock.return_value = test_data
    mock.get_page_data = AsyncMock(return_value=test_data)
    monkeypatch.setattr(patch_path, mock.get_page_data)

    mock.foia_fetcher = MagicMock()
    monkeypatch.setattr(module_path, mock.foia_fetcher)


    return mock

# TODO: Broken; fix or replace
# @pytest.mark.asyncio
# async def test_muckrock_all_foia_requests_collector(patch_muckrock_full_search_collector):
#     mock = patch_muckrock_full_search_collector
#     collector = MuckrockAllFOIARequestsCollector(
#         batch_id=1,
#         dto=MuckrockAllFOIARequestsCollectorInputDTO(
#             start_page=1,
#             total_pages=2
#         ),
#         logger=AsyncMock(spec=AsyncCoreLogger),
#         adb_client=AsyncMock(spec=AsyncDatabaseClient),
#         raise_error=True
#     )
#     await collector.run()
#
#     mock.get_page_data.assert_called_once_with(mock.foia_fetcher.return_value, 1, 2)
#
#     collector.adb_client.insert_urls.assert_called_once_with(
#         url_infos=[
#             URLInfo(
#                 url='https://include.com/1',
#                 collector_metadata={'absolute_url': 'https://include.com/1', 'title': 'keyword'},
#             ),
#             URLInfo(
#                 url='https://include.com/2',
#                 collector_metadata={'absolute_url': 'https://include.com/2', 'title': 'keyword'},
#             ),
#             URLInfo(
#                 url='https://include.com/3',
#                 collector_metadata={'absolute_url': 'https://include.com/3', 'title': 'lemon'},
#             ),
#         ],
#         batch_id=1
#     )
