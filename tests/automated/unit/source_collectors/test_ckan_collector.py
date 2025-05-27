import json
import pickle
from unittest.mock import MagicMock, AsyncMock

import pytest

from db.AsyncDatabaseClient import AsyncDatabaseClient
from core.AsyncCoreLogger import AsyncCoreLogger
from source_collectors.ckan.CKANCollector import CKANCollector
from source_collectors.ckan.DTOs import CKANInputDTO


@pytest.fixture
def mock_ckan_collector_methods(monkeypatch):
    mock = AsyncMock()

    mock_path = "source_collectors.ckan.CKANCollector.CKANCollector.get_results"
    with open("tests/test_data/ckan_get_result_test_data.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    mock.get_results = AsyncMock()
    mock.get_results.return_value = data
    monkeypatch.setattr(mock_path, mock.get_results)

    mock_path = "source_collectors.ckan.CKANCollector.CKANCollector.add_collection_child_packages"
    with open("tests/test_data/ckan_add_collection_child_packages.pkl", "rb") as f:
        data = pickle.load(f)

    mock.add_collection_child_packages = AsyncMock()
    mock.add_collection_child_packages.return_value = data
    monkeypatch.setattr(mock_path, mock.add_collection_child_packages)



    yield mock

@pytest.mark.asyncio
async def test_ckan_collector(mock_ckan_collector_methods):
    mock = mock_ckan_collector_methods

    collector = CKANCollector(
        batch_id=1,
        dto=CKANInputDTO(),
        logger=AsyncMock(spec=AsyncCoreLogger),
        adb_client=AsyncMock(spec=AsyncDatabaseClient),
        raise_error=True
    )
    await collector.run()

    mock.get_results.assert_called_once()
    mock.add_collection_child_packages.assert_called_once()

    collector.adb_client.insert_urls.assert_called_once()
    url_infos = collector.adb_client.insert_urls.call_args[1]['url_infos']
    assert len(url_infos) == 2560
    first_url_info = url_infos[0]
    assert first_url_info.url == 'https://catalog.data.gov/dataset/crash-reporting-drivers-data'
    assert first_url_info.collector_metadata['submitted_name'] == 'Crash Reporting - Drivers Data'

    last_url_info = url_infos[-1]
    assert last_url_info.url == 'https://data.houstontx.gov/dataset/houston-police-department-crime-statistics'
    assert last_url_info.collector_metadata["description"] == 'Multiple datasets related to Houston Police Department Crime Stats'

