# Test Cases
import json
from unittest.mock import patch
from urllib.parse import quote_plus

from common_crawler.crawler import CommonCrawler
from common_crawler.argparser import valid_common_crawl_id

# region CommonCrawler

# Mock data
mock_search_response = json.dumps({
    "pages": 10,
    "records": [{"url": "http://example.com"}, {"url": "http://example.com/page2"}]
})


@patch('requests.get')
def test_get_number_of_pages(mock_get):
    """
    Test that the get_number_of_pages method calls the expected URL
    and returns the expected number of pages
    """
    mock_get.return_value.status_code = 200
    mock_get.return_value.text = '{"pages": 2}'

    crawler = CommonCrawler()
    crawler.get_number_of_pages("http://example.com")

    # Assert that the mocked get method was called with the expected URL
    assert mock_get.called
    encoded_url = quote_plus("http://example.com")
    expected_url = f"{crawler.CC_INDEX_SERVER}{crawler.INDEX_NAME}?url={encoded_url}&output=json&showNumPages=true"
    mock_get.assert_called_with(expected_url)


@patch('requests.get')
def test_search_cc_index(mock_get):
    """
    Test that the search_cc_index method returns the expected records
    """
    mock_get.return_value.status_code = 200
    mock_get.return_value.text = mock_search_response

    crawler = CommonCrawler()
    result = crawler.search_common_crawl_index("http://example.com")

    assert len(result[0]['records']) == 2  # Assuming the mock response contains 2 records
    assert result[0]['records'][0]['url'] == "http://example.com"


def test_get_urls_with_keyword():
    """
    Test that the get_urls_with_keyword method returns the expected URLs
    """
    records = [
        {"url": "http://example.com"},
        {"url": "http://example.com/page2"},
        {"url": "http://test.com"}
    ]
    urls = CommonCrawler.get_urls_with_keyword(records, "example")
    assert len(urls) == 2
    assert "http://test.com" not in urls


# endregion CommonCrawler

# region Common Crawler Manager

def test_crawl_id_validation():
    """
    Test that the valid_common_crawl_id function properly detects
    valid and invalid crawl IDs
    """

    valid_crawl_id = "CC-MAIN-2023-50"
    invalid_crawl_id = "CC-MAIN-202"

    assert valid_common_crawl_id(valid_crawl_id)
    assert not valid_common_crawl_id(invalid_crawl_id)


# endregion CommonCrawlerManager
