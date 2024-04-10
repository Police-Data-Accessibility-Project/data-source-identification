import csv
from typing import List
from unittest.mock import MagicMock

import pytest
from pytest_postgresql import factories

from agency_homepage_searcher.agency_info import AgencyInfo
from agency_homepage_searcher.google_searcher import GoogleSearcher
from agency_homepage_searcher.homepage_searcher import HomepageSearcher, SearchResults
from util.db_manager import DBManager
from util.huggingface_api_manager import HuggingFaceAPIManager

FAKE_SEARCH_ROW_COUNT = 10


@pytest.fixture
def google_searcher(mocker):
    api_key = "test_api_key"
    cse_id = "test_cse_id"
    mock_service = mocker.patch("agency_homepage_searcher.google_searcher.build")

    # Create a mock for the Google API service object and set it as the return_value for the 'build' method
    mock_google_api_service = mocker.Mock()
    mock_service.return_value = mock_google_api_service
    return GoogleSearcher(api_key, cse_id)


def get_fake_agency_info() -> AgencyInfo:
    """
    Retr
    Returns:

    """
    return AgencyInfo(
        agency_name="Agency Police Agency",
        city="Cityopolis",
        state="PA",  # Must be an actual state because it is put in the STATE_ISO_TO_NAME_DICT in homepage_searcher.py
        county="Horborgor",
        zip_code="31415",
        website=None,
        agency_type="Police Agency",
        agency_id="abcdefghijklmnop"
    )


def convert_agency_info_to_list(agency_info: AgencyInfo) -> list:
    return [
        agency_info.agency_name,  # 0
        agency_info.agency_type,  # 1
        agency_info.state,  # 2
        agency_info.city,  # 3
        agency_info.county,  # 4
        agency_info.agency_id,  # 5
        agency_info.website,  # 6
        agency_info.zip_code  # 7
    ]


def validate_search_query(query_string):
    agency_info_list = convert_agency_info_to_list(get_fake_agency_info())
    for item in agency_info_list:
        if item is None:
            continue
        assert item in query_string, f"Item {item} not found in query string {query_string}"


def validate_update_search_cache(search_results: list[SearchResults]):
    agency_id = get_fake_agency_info().agency_id
    assert len(search_results) == 1
    assert agency_id == search_results[0].agency_id, f"Agency ID {agency_id} not in expected argument ({search_results[0].agency_id})"


def mock_database_query(query_string):
    return convert_agency_info_to_list(get_fake_agency_info())


def mock_search(q, cx):
    # Validate query is correct
    validate_search_query(q)

    # Return fake data
    return get_fake_search_data()


def get_fake_search_data():
    """
    Generate fake search data
    Returns:

    """
    fake_search_data = {'items': []}
    for i in range(1, FAKE_SEARCH_ROW_COUNT + 1):
        number = i
        # ASCII value of 'a' is 97, so we add i - 1 to it to get the incremental letter
        letter = chr(97 + (i - 1) % 26)  # Use modulo 26 to loop back to 'a' after 'z'
        fake_search_data['items'].append(
            {
                'link': f'https://www.example.com/{number}',
                'snippet': f'This snippet contains the letter {letter}'
            }
        )
    return fake_search_data


def validate_upload_to_huggingface(search_results: List[SearchResults]) -> None:
    fake_search_data_list = get_fake_search_data()['items']
    fake_agency_id = get_fake_agency_info().agency_id

    # Check there is only one search result
    assert len(search_results) == 1, "There should be only one search result pass to upload_to_huggingface"
    search_result = search_results[0]
    assert search_result.agency_id == fake_agency_id, f"Search result agency id should match {fake_agency_id}, is {search_result.agency_id}"
    assert len(
        search_result.search_results) == FAKE_SEARCH_ROW_COUNT, f"Number of search results should be {FAKE_SEARCH_ROW_COUNT}, is {len(search_result.search_results)}"
    for i in range(FAKE_SEARCH_ROW_COUNT):
        fake_search_data = fake_search_data_list[i]
        possible_homepage_url = search_result.search_results[i]
        assert fake_search_data[
                   'link'] == possible_homepage_url.url, f"Search result link {fake_search_data['link']} should match {possible_homepage_url.url}"
        assert fake_search_data[
                   'snippet'] == possible_homepage_url.snippet, f"Search result snippet {fake_search_data['snippet']} should match {possible_homepage_url.snippet}"


def test_agency_homepage_searcher_integration(monkeypatch, google_searcher):
    # Patch Google Searcher so that search call returns fake data
    google_searcher.service.cse().list().execute.return_value = get_fake_search_data()

    homepage_searcher = HomepageSearcher(
        search_engine=google_searcher,
        database_manager=MagicMock(spec=DBManager),
        huggingface_api_manager=MagicMock(spec=HuggingFaceAPIManager)
    )

    # Mock methods in homepage searcher that interface with external sources
    #   update_search_cache - verifies proper IDs
    #   get_agencies_without_homepage_urls - return list of fake agency info
    #   upload_to_huggingface - verifies proper search results
    homepage_searcher.update_search_cache = validate_update_search_cache
    homepage_searcher.get_agencies_without_homepage_urls = lambda: [get_fake_agency_info()]
    homepage_searcher.upload_to_huggingface = validate_upload_to_huggingface

    homepage_searcher.search_and_upload(1)

