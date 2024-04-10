import os
from googleapiclient.errors import HttpError
from unittest.mock import Mock
import csv
import pytest
from pathlib import Path
from unittest.mock import MagicMock

from agency_homepage_searcher.homepage_searcher import HomepageSearcher, AgencyInfo, GoogleSearcher, \
    PossibleHomepageURL, SearchResultEnum

from agency_homepage_searcher.homepage_searcher import (
    SQL_UPDATE_CACHE,
    SearchResults,
    QuotaExceededError,
)


class TestGoogleSearcher:

    @pytest.fixture
    def google_searcher(self, mocker):
        api_key = "test_api_key"
        cse_id = "test_cse_id"
        mock_service = mocker.patch("agency_homepage_searcher.google_searcher.build")

        # Create a mock for the Google API service object and set it as the return_value for the 'build' method
        mock_google_api_service = mocker.Mock()
        mock_service.return_value = mock_google_api_service
        return GoogleSearcher(api_key, cse_id)

    def test_init(self, google_searcher):
        assert google_searcher.api_key == "test_api_key"
        assert google_searcher.cse_id == "test_cse_id"

    def test_init_with_None_api_key_or_cse_id(self):
        with pytest.raises(RuntimeError):
            GoogleSearcher(None, "test_cse_id")
        with pytest.raises(RuntimeError):
            GoogleSearcher("test_api_key", None)

    def test_search(self, google_searcher):
        google_searcher.service.cse().list().execute.return_value = {
            'items': 'result'
        }
        items = google_searcher.search("query")
        assert items == "result"

    def test_search_with_http_error_quota_exceeded(self, google_searcher):
        google_searcher.service.cse().list().execute.side_effect = HttpError(Mock(), "Quota exceeded".encode())
        with pytest.raises(QuotaExceededError):
            google_searcher.search("query")

    def test_search_with_http_error(self, google_searcher):
        google_searcher.service.cse().list().execute.side_effect = HttpError(Mock(), "error".encode())
        with pytest.raises(RuntimeError):
            google_searcher.search("query")


class TestHomepageSearcher:

    @pytest.fixture
    def test_homepage_searcher(mocker):
        return HomepageSearcher(
            search_engine=Mock(),
            database_manager=Mock(),
            huggingface_api_manager=Mock())

    def test_search_and_upload(self, mocker, test_homepage_searcher, monkeypatch):
        # Provide fake array for "get_agencies_without_homepage_urls"
        mock_agency_info_list = [MagicMock(), MagicMock(), MagicMock()]
        mock_get_agencies_without_homepage_urls = mocker.Mock(return_value=mock_agency_info_list)
        test_homepage_searcher.get_agencies_without_homepage_urls = mock_get_agencies_without_homepage_urls

        # Provide fake array of Search Results for "search_until_limit_reached" method
        mock_search_results = []
        mock_agency_ids = []
        for i in range(3):
            mock_search_result = MagicMock(spec=SearchResults)
            mock_search_result.agency_id = i
            mock_search_results.append(mock_search_result)
            mock_agency_ids.append(i)
        mock_search_until_limit_reached = mocker.Mock(return_value=mock_search_results)
        test_homepage_searcher.search_until_limit_reached = mock_search_until_limit_reached

        # Mock upload_to_huggingface method
        mock_upload_to_huggingface = MagicMock(return_value=None)
        test_homepage_searcher.upload_to_huggingface = mock_upload_to_huggingface

        # Mock update_search_cache method
        mock_update_search_cache = MagicMock()
        test_homepage_searcher.update_search_cache = mock_update_search_cache

        test_homepage_searcher.search_and_upload(max_searches=10)

        # Test all mocked functions called with proper arguments
        mock_get_agencies_without_homepage_urls.assert_called_once()
        mock_search_until_limit_reached.assert_called_once_with(agency_info_list=mock_agency_info_list, max_searches=10)
        mock_upload_to_huggingface.assert_called_once()
        mock_update_search_cache.assert_called_once_with(mock_agency_ids)

    def test_upload_to_huggingface(self, mocker, test_homepage_searcher, monkeypatch):
        test_homepage_searcher.huggingface_api_manager.repo_id = "TestOrg/TestDataset"

        # Mock write_to_temporary_csv method
        mock_file_path = MagicMock(spec=Path, return_value="fake_dir/fake_name.csv")
        mock_write_to_temporary_csv = MagicMock(return_value=mock_file_path)
        test_homepage_searcher.write_to_temporary_csv = mock_write_to_temporary_csv

        # Mock get_filename_friendly_timestamp_method
        mock_filename_friendly_timestamp = "YYYY-MM-DD_hh-mm-ss"
        monkeypatch.setattr(
            target='agency_homepage_searcher.homepage_searcher.get_filename_friendly_timestamp',
            name=lambda: mock_filename_friendly_timestamp
        )

        # Run upload_to_huggingface with mock methods
        mock_search_results = [MagicMock(), MagicMock(), MagicMock()]
        test_homepage_searcher.upload_to_huggingface(mock_search_results)

        # Assert all functions called with necessary arguments
        mock_write_to_temporary_csv.assert_called_with(mock_search_results)
        mock_file_path.unlink.assert_called_once()
        test_homepage_searcher.huggingface_api_manager.upload_file.assert_called_once_with(
            local_file_path=mock_file_path,
            repo_file_path=f"/data/search_results_{mock_filename_friendly_timestamp}.csv"
        )

    def test_search_agency_info_success(self, test_homepage_searcher):
        expected_result = MagicMock(spec=SearchResults)

        mock_search = MagicMock(return_value=expected_result)
        test_homepage_searcher.search = mock_search

        mock_agency_info = MagicMock(spec=AgencyInfo)
        result = test_homepage_searcher._try_search_agency_info(mock_agency_info)

        assert result == expected_result

    def test_search_agency_info_exception(self, test_homepage_searcher):
        expected_result = []
        mock_agency_info = MagicMock(spec=AgencyInfo)

        mock_search = MagicMock(return_value=MagicMock(spec=SearchResults))
        mock_search.side_effect = Exception
        test_homepage_searcher.search = mock_search

        result = test_homepage_searcher._try_search_agency_info(mock_agency_info)

        assert result == expected_result

    def test_update_search_cache(self, test_homepage_searcher):
        # Create test parameter
        test_agency_ids = ["test1", "test2", "test3"]

        # Configure the Mock DB manager to ensure update SQL is called
        test_homepage_searcher.database_manager.executemany = MagicMock()

        # Call the function with our test data
        test_homepage_searcher.update_search_cache(test_agency_ids)

        # Check that executemany was called with the expected arguments
        test_homepage_searcher.database_manager.executemany.assert_called_once_with(SQL_UPDATE_CACHE,
                                                                                    [(agency_id,) for agency_id in
                                                                                     test_agency_ids])

    def test_write_search_result_to_csv_success(self, test_homepage_searcher):
        search_results = [PossibleHomepageURL("http://example.com", "example snippet"),
                          PossibleHomepageURL("http://test.com", "test snippet")]
        search_result = Mock()
        search_result.agency_id = "test_agency"
        search_result.search_results = search_results

        writer_mock = MagicMock()

        HomepageSearcher._write_search_result_to_csv(search_result, writer_mock)

        assert writer_mock.writerow.call_count == 2

    def test_write_search_result_to_csv_failure(self, test_homepage_searcher):
        search_results = [PossibleHomepageURL("http://example.com", "example snippet"),
                          PossibleHomepageURL("http://test.com", "test snippet")]
        search_result = Mock()
        search_result.agency_id = "test_agency"
        search_result.search_results = search_results

        writer_mock = MagicMock()
        writer_mock.writerow.side_effect = Exception()

        with pytest.raises(Exception):
            HomepageSearcher._write_search_result_to_csv(search_result, writer_mock)

    @pytest.fixture()
    def tmp_csv_setup_teardown(self):
        yield open(file='test_tmpfile.csv', mode='w', encoding='utf-8')
        os.remove('test_tmpfile.csv')

    def test_write_to_temporary_csv(self, test_homepage_searcher, monkeypatch, tmp_csv_setup_teardown):
        open_tmpfile_csv_lambda = MagicMock(return_value=tmp_csv_setup_teardown)
        monkeypatch.setattr(
            "agency_homepage_searcher.homepage_searcher.tempfile.NamedTemporaryFile"
            , open_tmpfile_csv_lambda)

        test_agency_id = "test_agency"
        mock_search_results = [
            MagicMock(agency_id=test_agency_id, url="https://example.com", snippet="An example website."),
            MagicMock(agency_id=test_agency_id, url="https://test.com", snippet="A test website."),
            MagicMock(agency_id=test_agency_id, url="https://python.com", snippet="Python's official website."),
        ]
        search_results = [SearchResults(test_agency_id, mock_search_results, SearchResultEnum.FOUND_RESULTS)]

        tmp_filepath = test_homepage_searcher.write_to_temporary_csv(search_results)
        assert isinstance(tmp_filepath, Path)

        with open(tmp_filepath, 'r') as f:
            reader = csv.reader(f)
            header = next(reader)
            assert header == ["agency_id", "url", "snippet"]

            row_count = 0
            for i, row in enumerate(reader):
                assert row == [search_results[0].agency_id, mock_search_results[i].url, mock_search_results[i].snippet]
                row_count += 1
            assert row_count == 3

    @pytest.fixture
    def mock_agencies(self):
        return [MagicMock(spec=AgencyInfo) for _ in range(10)]

    @pytest.fixture
    def mock_search_results(self):
        return [MagicMock(spec=SearchResults) for _ in range(10)]

    def test_reach_max_searches(self, test_homepage_searcher, mock_agencies, mock_search_results):
        # Set the search method to return a search result each time
        test_homepage_searcher.search = MagicMock(side_effect=mock_search_results)
        results = test_homepage_searcher.search_until_limit_reached(mock_agencies, max_searches=5)
        assert len(results) == 5

    def test_handle_exception(self, test_homepage_searcher, mock_agencies, mock_search_results):
        # Set the search method to raise an exception
        test_homepage_searcher.search = MagicMock(side_effect=Exception())
        test_homepage_searcher._handle_search_error = MagicMock()
        results = test_homepage_searcher.search_until_limit_reached(mock_agencies, max_searches=5)
        test_homepage_searcher._handle_search_error.assert_called()

    def test_quota_exceeded(self, test_homepage_searcher, mock_agencies, mock_search_results):
        # Set the search method to return None one time and search results the rest of the times
        test_homepage_searcher.search = MagicMock(side_effect=[None] + mock_search_results)
        results = test_homepage_searcher.search_until_limit_reached(mock_agencies, max_searches=5)
        assert len(results) == 0

    @pytest.fixture
    def mock_agency_info(self):
        mock_agency_info = MagicMock(spec=AgencyInfo)
        mock_agency_info.agency_id = 'id'
        mock_agency_info.name = 'name'
        return mock_agency_info

    def test_search_with_results(self, test_homepage_searcher, mock_agency_info):
        test_homepage_searcher.search_engine.search = MagicMock(
            return_value=[{'link': 'http://test.com', 'snippet': 'test snippet'}])

        result = test_homepage_searcher.search(mock_agency_info)

        assert isinstance(result, SearchResults)
        assert result.agency_id == 'id'
        assert len(result.search_results) == 1
        assert result.search_results[0].url == 'http://test.com'

    def test_search_without_results(self, test_homepage_searcher, mock_agency_info):
        test_homepage_searcher.search_engine.search = MagicMock(return_value=[])

        result = test_homepage_searcher.search(mock_agency_info)

        assert isinstance(result, SearchResults)
        assert result.agency_id == 'id'
        assert len(result.search_results) == 0

    def test_search_quota_exceeded(self, test_homepage_searcher, mock_agency_info):
        test_homepage_searcher.search_engine.search = MagicMock(side_effect=QuotaExceededError)

        result = test_homepage_searcher.search(mock_agency_info)

        assert result is None

    @pytest.fixture
    def sample_valid_agency_row(self, ):
        return ['Test Agency', 'Federal', 'CA', 'San Francisco', 'Alameda',
                '5141', '5141', '94105']

    @pytest.fixture
    def sample_invalid_agency_row(self):
        return ['Invalid Agency', 'Federal', 'XX', 'Invalid City', 'Invalid County',
                '9999', '9999', '99999']

    def test_create_agency_info_with_valid_agency_row(self, sample_valid_agency_row):
        expected_agency_info = AgencyInfo(
            agency_name='Test Agency',
            city='San Francisco',
            state='California',
            county='Alameda',
            zip_code='94105',
            website=None,
            agency_type='Federal',
            agency_id='5141'
        )
        assert HomepageSearcher.create_agency_info(sample_valid_agency_row) == expected_agency_info

    def test_create_agency_info_with_invalid_agency_row(self, sample_invalid_agency_row):
        with pytest.raises(ValueError):
            HomepageSearcher.create_agency_info(sample_invalid_agency_row)


def test_agency_info_get_search_string_character_strip():
    """
    Test that the get_search_string_character strip does not include disallowed characters
    """
    disallowed_characters = ['[', ']', '\'', '\"', ')', '(']
    agency_info = AgencyInfo(
        agency_name='Agency',
        city='San Francisco',
        state='California',
        county='Alameda',
        zip_code='94105',
        website=None,
        agency_type='Federal',
        agency_id='5141'
    )
    for character in disallowed_characters:
        agency_info.agency_name += character
    search_string = agency_info.get_search_string()
    for character in disallowed_characters:
        assert character not in search_string, f'The character {character} is erroneously included in the search string {search_string}'

