# Test Cases
import json
from unittest.mock import patch, mock_open
from urllib.parse import quote_plus

import pytest
from unittest.mock import MagicMock

from common_crawler.crawler import CommonCrawlerManager, CommonCrawler
from common_crawler.cache import CommonCrawlerCacheObject, CommonCrawlerCacheManager


# region CommonCrawlerCacheObject
@pytest.mark.parametrize("index, url, search_term, page_count", [
    ("CC-MAIN-2020-24", "http://example.com", "example", 0),
    ("CC-MAIN-2019-47", "https://anotherexample.com", "test", 5)
])
def test_common_crawler_cache_object_creation(index, url, search_term, page_count):
    """
    Test that the CommonCrawlerCacheObject is created with the expected attributes
    """
    obj = CommonCrawlerCacheObject(index, url, search_term, page_count)
    assert obj.index == index
    assert obj.url == url
    assert obj.search_term == search_term
    assert obj.last_page == page_count


def test_to_dict():
    """
    Test that the to_dict method returns the expected dictionary
    """
    obj = CommonCrawlerCacheObject("CC-MAIN-2020-24", "http://example.com", "example", 3)
    expected_dict = {
        "index": "CC-MAIN-2020-24",
        "url": "http://example.com",
        "search_term": "example",
        "count": 3
    }
    assert obj.to_dict() == expected_dict


def test_from_dict():
    """
    Test that the from_dict method creates a CommonCrawlerCacheObject
    with the expected attributes
    """
    input_dict = {
        "index": "CC-MAIN-2020-24",
        "url": "http://example.com",
        "search_term": "example",
        "count": 3
    }
    obj = CommonCrawlerCacheObject.from_dict(input_dict)
    assert obj.index == input_dict["index"]
    assert obj.url == input_dict["url"]
    assert obj.search_term == input_dict["search_term"]
    assert obj.last_page == input_dict["count"]


# endregion CommonCrawlerCacheObject

# region CommonCrawlerCache

# Test Cases
def test_add_and_get():
    """
    Test that the add and get methods work as expected
    """
    cache = CommonCrawlerCacheManager(storage=MagicMock())
    index = "CC-MAIN-2020-24"
    url = "http://example.com"
    search_term = "example"

    # Test adding a new search to the cache
    cache.add(index, url, search_term)
    cached_object = cache.get(index, url, search_term)

    assert cached_object.index == index
    assert cached_object.url == url
    assert cached_object.search_term == search_term
    assert cached_object.last_page == 0  # Should be initialized to 0



def test_save_cache():
    """
    Test that the save_cache method calls the save_cache method of the storage
    """
    cache = CommonCrawlerCacheManager(storage=MagicMock())
    cache.add("CC-MAIN-2020-24", "http://example.com", "example")

    cache.save_cache()
    cache.storage.save_cache.assert_called_once()


def test_load_or_create_cache():
    """
    Test that the load_or_create_cache method loads the cache from storage
    when it exists, and creates a new cache when it does not
    """
    # Create a MagicMock for the storage
    mock_storage = MagicMock()

    # Set the return value for the load_cache method
    mock_storage.load_cache.return_value = {
        "CC-MAIN-2020-24": {
            "http://example.com": {
                "example": {
                    'last_page_crawled': 3
                }
            }
        }
    }
    cache = CommonCrawlerCacheManager(storage=mock_storage)
    cache.load_or_create_cache()

    assert "example" in cache.cache["CC-MAIN-2020-24"]["http://example.com"]
    cached_object = cache.cache["CC-MAIN-2020-24"]["http://example.com"]["example"]
    assert cached_object.last_page == 3


# endregion CommonCrawlerCacheManager

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

# region CommonCrawlerManager
@patch('common_crawler.cache.CommonCrawlerCacheManager')
@patch('common_crawler.crawler.CommonCrawler')
def test_reset_cache(MockCommonCrawler, MockCommonCrawlerCacheManager):
    """
    Test that the cache is reset when the reset_cache method is called
    """
    manager = CommonCrawlerManager(
        cache_storage=MagicMock()
    )
    manager.reset_cache()
    assert manager.cache.cache == {}  # Ensure the cache is reset

@patch('common_crawler.crawler.CommonCrawlerCacheManager', return_value=MagicMock())
def test_crawl_id_validation(mocked_cache_manager):
    """
    Test that the crawl method raises a ValueError when
    an invalid crawl_id is provided
    """
    manager = CommonCrawlerManager(
        cache_storage=MagicMock()
    )
    valid_crawl_id = "CC-MAIN-2023-50"
    invalid_crawl_id = "CC-MAIN-202"

    # Valid crawl_id should not raise an error
    try:
        manager.crawl(valid_crawl_id, "http://example.com", "example", 1)
    except ValueError:
        pytest.fail("crawl raised ValueError unexpectedly!")

    # Invalid crawl_id should raise ValueError
    with pytest.raises(ValueError):
        manager.crawl(invalid_crawl_id, "http://example.com", "example", 1)


@patch.object(CommonCrawler, 'search_common_crawl_index', return_value=[{"url": "http://example.com"}])
@patch.object(CommonCrawlerCacheManager, 'get', return_value=CommonCrawlerCacheObject("CC-MAIN-2023-50", "http://example.com", "example", 0))
@patch.object(CommonCrawlerCacheManager, 'save_cache')
def test_crawl(mock_save_cache, mock_get, mock_search_cc_index):
    """
    Test that the crawl method calls the
    expected methods with the expected arguments
    """
    manager = CommonCrawlerManager(
        cache_storage=MagicMock()
    )
    crawl_id = "CC-MAIN-2023-50"
    url = "http://example.com"
    keyword = "example"
    num_pages = 1

    results = manager.crawl(
        crawl_id=crawl_id,
        search_term=url,
        keyword=keyword,
        num_pages=num_pages)

    try:
        mock_get.assert_called_with(crawl_id, url, keyword)
    except AssertionError:
        actual_args = mock_get.call_args
        raise AssertionError(f"mock_get was not called with the expected arguments. It was called with {actual_args}")

    try:
        mock_save_cache.assert_called_once()
    except AssertionError:
        raise AssertionError("mock_save_cache was not called exactly once")

    try:
        mock_search_cc_index.assert_called_with(url, 1)
    except AssertionError:
        actual_args = mock_search_cc_index.call_args
        raise AssertionError(f"mock_search_cc_index was not called with the expected arguments. It was called with {actual_args}")
    # Verify results
    assert len(results) == 1, "Expected 1 result"
    assert results[0].url == "http://example.com"
    assert results[0].index == crawl_id
    assert results[0].search_term == url
    assert results[0].page == 1
    assert results[0].keyword == keyword


# endregion CommonCrawlerManager
