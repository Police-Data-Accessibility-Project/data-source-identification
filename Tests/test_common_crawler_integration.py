import json
import tempfile
from unittest.mock import mock_open, patch

import pytest

from common_crawler.main import main
from common_crawler.cache import CacheStorage, CommonCrawlerCacheManager


def test_cache_persistence():
    """
    Test that the cache can be saved to and loaded from a file
    """

    with tempfile.TemporaryDirectory() as tmp_dir:
        # Create a cache and add data to it
        cache = CommonCrawlerCacheManager(
            storage=CacheStorage(
                file_name="test_cache.json",
                directory=tmp_dir,
            )
        )
        cache.add("CC-MAIN-2020-24", "http://example.com", "example")
        cache.cache["CC-MAIN-2020-24"]["http://example.com"]["example"].count = 3

        # Save the cache to a file
        cache.save_cache()

        # Recreate the cache and load the data from the file
        cache = CommonCrawlerCacheManager(
            storage=CacheStorage(
                file_name="test_cache.json",
                directory=tmp_dir,
            )
        )

        # Assert that the loaded cache matches the original data
        assert cache.cache["CC-MAIN-2020-24"]["http://example.com"]["example"].count == 3
        # assert cache.cache == mock_data, "Loaded cache does not match original data"

        # Clean up the test file


def test_main_with_valid_args(mocker):
    """
    Test the main function with valid arguments
    """
    mock_parse_args = mocker.patch('common_crawler.main.parse_args')
    mock_args = mock_parse_args.return_value
    mock_args.common_crawl_id = 'test_id'
    mock_args.url = 'http://testurl.com'
    mock_args.search_term = 'test_term'
    mock_args.pages = 2
    mock_args.output = 'test_output.txt'
    mock_args.reset_cache = True

    # Mock the CommonCrawlerManager to avoid actual web requests
    mock_manager = mocker.Mock()
    mock_manager.crawl.return_value = ['http://example.com']
    mocker.patch('common_crawler.main.CommonCrawlerManager', return_value=mock_manager)

    # Mock file writing if necessary
    mocker.patch("builtins.open", mocker.mock_open())

    # Call main with test arguments
    main()

    # Assertions to verify behavior
    mock_manager.crawl.assert_called_once_with('test_id', 'http://testurl.com', 'test_term', 2)
    open.assert_called_once_with('test_output.txt', 'w')
    # Add more assertions as necessary