import json
import tempfile
import os
import pytest
from unittest.mock import mock_open, patch
from source_text_collector.RootURLCache import RootURLCache  # Adjust import according to your package structure


@pytest.fixture
def temp_file():
    # Setup: Create a temporary file and immediately close it to avoid locking issues
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.close()  # Close the file so it's not locked by the current process
    yield temp_file.name  # This is used by the test
    # Teardown: Delete the temporary file
    os.remove(temp_file.name)


@pytest.fixture
def cache(temp_file):
    # Setup: Create a cache instance with a temporary file
    cache = RootURLCache(cache_file=temp_file)
    return cache


def test_load_cache_no_file(mocker):
    """Test loading the cache when the file does not exist."""
    mocker.patch('os.path.exists', return_value=False)
    cache = RootURLCache().load_cache()
    assert cache == {}, "Cache should be empty if file does not exist"


def test_load_cache_with_file(mocker):
    """Test loading the cache from an existing file."""
    mock_data = '{"https://example.com": "Example Domain"}'
    mocker.patch('os.path.exists', return_value=True)
    mocker.patch('builtins.open', mock_open(read_data=mock_data))
    cache = RootURLCache().load_cache()
    assert cache == json.loads(mock_data), "Cache should match the content of the file"


def test_save_cache(temp_file):
    """Test saving the cache to a file."""
    with patch('os.path.exists', return_value=False):
        cache = RootURLCache(cache_file=temp_file)
        cache.cache = {'https://example.com': 'Example Domain'}
        cache.save_cache()

    with open(temp_file, 'r') as f:
        file_contents = f.read()
        expected_contents = json.dumps(cache.cache, indent=4)
        assert file_contents == expected_contents


def test_get_title_not_in_cache(mocker, cache):
    """Test retrieving a title not in cache, simulating a web request."""
    mock_response = mocker.Mock()
    mock_response.text = '<html><head><title>Example Domain</title></head></html>'
    mocker.patch('requests.get', return_value=mock_response)
    title = cache.get_title('https://example.com')
    assert title == 'Example Domain', "Title should be retrieved from the web"


def test_get_title_in_cache(cache):
    """Test retrieving a title that is already in cache."""
    cache.cache = {'https://example.com': 'Example Domain'}
    title = cache.get_title('https://example.com')
    assert title == 'Example Domain', "Title should be retrieved from the cache"


@pytest.mark.parametrize("url,expected_title", [
    ('http://www.example.com', 'Example Domain'),
    ('http://www.google.com', 'Google'),
    ('https://books.toscrape.com/catalogue/category/books/womens-fiction_9/index.html',
     'All products | Books to Scrape - Sandbox'),
    (
            'https://books.toscrape.com/catalogue/i-had-a-nice-time-and-other-lies-how-to-find-love-sht-like-that_814/index.html',
            'All products | Books to Scrape - Sandbox')
])
def test_actual_urls(url, expected_title, cache):
    """Test retrieving titles from actual URLs."""
    title = cache.get_title(url)
    assert title.strip() == expected_title
