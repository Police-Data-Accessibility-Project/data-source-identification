from unittest import mock
from unittest.mock import MagicMock, call

import pytest

from collector_db.DTOs.URLInfo import URLInfo
from collector_db.DatabaseClient import DatabaseClient
from collector_manager.enums import URLOutcome
from core.CoreLogger import CoreLogger
from source_collectors.muckrock.DTOs import MuckrockSimpleSearchCollectorInputDTO, \
    MuckrockCountySearchCollectorInputDTO, MuckrockAllFOIARequestsCollectorInputDTO
from source_collectors.muckrock.classes.MuckrockCollector import MuckrockSimpleSearchCollector, \
    MuckrockCountyLevelSearchCollector, MuckrockAllFOIARequestsCollector
from source_collectors.muckrock.classes.fetch_requests.FetchRequestBase import FetchRequest
from source_collectors.muckrock.classes.muckrock_fetchers.FOIAFetcher import FOIAFetchRequest, FOIAFetcher


@pytest.fixture
def patch_muckrock_fetcher(monkeypatch):
    patch_path = "source_collectors.muckrock.classes.muckrock_fetchers.MuckrockFetcher.MuckrockFetcher.fetch"
    inner_test_data = [
        {"absolute_url": "https://include.com/1", "title": "keyword"},
        {"absolute_url": "https://include.com/2", "title": "keyword"},
        {"absolute_url": "https://exclude.com/3", "title": "lemon"},
    ]
    test_data = {
        "results": inner_test_data
    }
    mock = MagicMock()

    mock.return_value = test_data
    monkeypatch.setattr(patch_path, mock)
    return mock



def test_muckrock_simple_collector(patch_muckrock_fetcher):
    collector = MuckrockSimpleSearchCollector(
        batch_id=1,
        dto=MuckrockSimpleSearchCollectorInputDTO(
            search_string="keyword",
            max_results=2
        ),
        logger=mock.MagicMock(spec=CoreLogger),
        db_client=mock.MagicMock(spec=DatabaseClient),
        raise_error=True
    )
    collector.run()
    patch_muckrock_fetcher.assert_has_calls(
        [
            call(FOIAFetchRequest(page=1, page_size=100)),
        ]
    )
    collector.db_client.insert_urls.assert_called_once_with(
        url_infos=[
            URLInfo(
                url='https://include.com/1',
                collector_metadata={'absolute_url': 'https://include.com/1', 'title': 'keyword'},
            ),
            URLInfo(
                url='https://include.com/2',
                collector_metadata={'absolute_url': 'https://include.com/2', 'title': 'keyword'},
            )
        ],
        batch_id=1
    )


@pytest.fixture
def patch_muckrock_county_level_search_collector_methods(monkeypatch):
    patch_root = ("source_collectors.muckrock.classes.MuckrockCollector."
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
    mock.get_jurisdiction_ids = MagicMock(return_value=get_jurisdiction_ids_data)
    mock.get_foia_records = MagicMock(return_value=get_foia_records_data)
    monkeypatch.setattr(patch_path_get_jurisdiction_ids, mock.get_jurisdiction_ids)
    monkeypatch.setattr(patch_path_get_foia_records, mock.get_foia_records)
    return mock

def test_muckrock_county_search_collector(patch_muckrock_county_level_search_collector_methods):
    mock_methods = patch_muckrock_county_level_search_collector_methods

    collector = MuckrockCountyLevelSearchCollector(
        batch_id=1,
        dto=MuckrockCountySearchCollectorInputDTO(
            parent_jurisdiction_id=1,
            town_names=["test"]
        ),
        logger=MagicMock(spec=CoreLogger),
        db_client=MagicMock(spec=DatabaseClient),
        raise_error=True
    )
    collector.run()

    mock_methods.get_jurisdiction_ids.assert_called_once()
    mock_methods.get_foia_records.assert_called_once_with({"Alpha": 1, "Beta": 2})

    collector.db_client.insert_urls.assert_called_once_with(
        url_infos=[
            URLInfo(
                url='https://include.com/1',
                collector_metadata={'absolute_url': 'https://include.com/1', 'title': 'keyword'},
            ),
            URLInfo(
                url='https://include.com/2',
                collector_metadata={'absolute_url': 'https://include.com/2', 'title': 'keyword'},
            ),
            URLInfo(
                url='https://include.com/3',
                collector_metadata={'absolute_url': 'https://include.com/3', 'title': 'lemon'},
            ),
        ],
        batch_id=1
    )

@pytest.fixture
def patch_muckrock_full_search_collector(monkeypatch):
    patch_path = ("source_collectors.muckrock.classes.MuckrockCollector."
                  "MuckrockAllFOIARequestsCollector.get_page_data")
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
    mock = MagicMock()
    mock.return_value = test_data
    mock.get_page_data = MagicMock(return_value=test_data)
    monkeypatch.setattr(patch_path, mock.get_page_data)

    patch_path = ("source_collectors.muckrock.classes.MuckrockCollector."
                  "FOIAFetcher")
    mock.foia_fetcher = MagicMock()
    monkeypatch.setattr(patch_path, mock.foia_fetcher)


    return mock

def test_muckrock_all_foia_requests_collector(patch_muckrock_full_search_collector):
    mock = patch_muckrock_full_search_collector
    collector = MuckrockAllFOIARequestsCollector(
        batch_id=1,
        dto=MuckrockAllFOIARequestsCollectorInputDTO(
            start_page=1,
            total_pages=2
        ),
        logger=MagicMock(spec=CoreLogger),
        db_client=MagicMock(spec=DatabaseClient),
        raise_error=True
    )
    collector.run()

    mock.get_page_data.assert_called_once_with(mock.foia_fetcher.return_value, 1, 2)

    collector.db_client.insert_urls.assert_called_once_with(
        url_infos=[
            URLInfo(
                url='https://include.com/1',
                collector_metadata={'absolute_url': 'https://include.com/1', 'title': 'keyword'},
            ),
            URLInfo(
                url='https://include.com/2',
                collector_metadata={'absolute_url': 'https://include.com/2', 'title': 'keyword'},
            ),
            URLInfo(
                url='https://include.com/3',
                collector_metadata={'absolute_url': 'https://include.com/3', 'title': 'lemon'},
            ),
        ],
        batch_id=1
    )
