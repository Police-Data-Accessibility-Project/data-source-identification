import pytest
from agency_homepage_searcher.google_searcher import GoogleSearcher, QuotaExceededError
from googleapiclient.errors import HttpError
from unittest.mock import Mock

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
