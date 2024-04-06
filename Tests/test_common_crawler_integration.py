import csv
import json
import os
import shutil
import tempfile
import datetime
from unittest.mock import patch

import pytest

from common_crawler.csv_manager import CSVManager
from common_crawler.main import main, BATCH_HEADERS
from common_crawler.cache import CommonCrawlerCacheManager

class CSVData:

    def __init__(self, file_path: str):
        with open(file_path, 'r') as f:
            reader = csv.reader(f)
            self.headers = next(reader)
            self.rows = []
            for row in reader:
                row_dict = dict(zip(self.headers, row))  # Convert the row to a dictionary
                self.rows.append(row_dict)

def validate_csv(file_path, expected_values):
    """
    Validate that the CSV file contains the expected values
    Args:
        file_path:
        expected_values:

    Returns:

    """
    # Extract directory path from local_file_path
    directory = os.path.dirname(file_path)
    # Extract file name from local_file_path
    file_name = os.path.basename(file_path)

    # Create a dictionary mirroring the expected values,
    # with the column names as keys, and all values initialized to false
    found_dict = {column: False for column in expected_values.keys()}

    path = f"{directory}/{file_name}"
    csv_data = CSVData(path)

    for row in csv_data.rows:
        for column, expected_value in expected_values.items():
            if row[column] == expected_value:
                found_dict[column] = True

    return all(found_dict.values())

def test_cache_persistence():
    """
    Test that the cache can be saved to and loaded from a file
    """

    with tempfile.TemporaryDirectory() as tmp_dir:
        # Create a cache and add data to it
        cache = CommonCrawlerCacheManager(
            file_name="test_cache.json",
            directory=tmp_dir,
        )
        cache.upsert("CC-MAIN-2020-24", "http://example.com", "example", 3)

        # Save the cache to a file
        cache.save_cache()

        # Recreate the cache and load the data from the file
        cache = CommonCrawlerCacheManager(
            file_name="test_cache.json",
            directory=tmp_dir,
        )

        # Assert that the loaded cache matches the original data
        assert cache.cache["CC-MAIN-2020-24"]["http://example.com"]["example"] == 3
        # assert cache.cache == mock_data, "Loaded cache does not match original data"

        # Reset cache and verify that it is is empty
        cache.reset_cache()
        assert cache.cache == {}

        # Clean up the test file

def validate_csvs(local_file_path, repo_file_path):
    # Check that the output file was created, and contains the expected data

    assert validate_csv(local_file_path, {
        'url': 'http://police.com'
    }), "Output csv file does not contain expected data"
    assert validate_csv(local_file_path, {
        'url': 'http://police.com/page2'
    }), "Output csv file does not contain expected data"
    # Additionally validate that the previous output file does not exist
    assert not validate_csv(local_file_path, {
        'url': 'http://keyword.com'
    }), "Output csv file does not contain expected data"

def validate_csv_reset_cache(local_file_path, repo_file_path):
    # Check that the output file was created, and contains the expected data
    assert validate_csv(local_file_path, {
        'url': 'http://keyword.com'
    }), "Output csv file does not contain expected data"



@patch('util.huggingface_api_manager.HuggingFaceAPIManager.upload_file')
def test_main_with_valid_args(mock_upload_file, mocker, temp_dir):
    """
    Test the main function with valid arguments
    """

    # Replace the huggingface_api_manager upload_file function with one that
    # performs the validate_csvs function
    mock_upload_file.side_effect = validate_csv_reset_cache

    # Main uses datetime.now(): patch this to provide a single datetime
    mock_now = str(datetime.datetime(2022, 12, 12, 12, 0, 0))
    mocker.patch("common_crawler.main.get_current_time", return_value=mock_now)

    mock_parse_args = mocker.patch('common_crawler.main.parse_args')
    mock_args = mock_parse_args.return_value
    mock_args.common_crawl_id = 'CC-MAIN-9999-99'
    mock_args.url = '*.com'
    mock_args.keyword = 'keyword'
    mock_args.pages = 2
    mock_args.output_filename = 'test_output'
    mock_args.cache_filename = 'test_cache'
    mock_args.data_dir = temp_dir
    mock_args.reset_cache = True

    # Mock the CommonCrawler to avoid actual web requests
    common_crawler_results = [
        # This result, containing the search keyword should be returned in the final output
        [{
            'url': 'http://keyword.com'
        }],
        # This result, because it does not contain the keyword, should not
        [{
            'url': 'http://not-in-results.com'
        }]
    ]
    mock_search_cc_index = mocker.patch('common_crawler.crawler.CommonCrawlerManager.search_common_crawl_index')
    mock_search_cc_index.side_effect = common_crawler_results

    # Common crawler sleeps for five seconds during execution -- this avoids that.
    mock_sleep = mocker.patch('time.sleep')
    mock_sleep.side_effect = lambda _: None

    # Call main with test arguments
    main()


    # Check that the cache file was created, and contains the expected data
    with open(f'{temp_dir}/test_cache.json', 'r') as file:
        cache = json.load(file)
        assert 'CC-MAIN-9999-99' in cache
        assert '*.com' in cache['CC-MAIN-9999-99']
        assert 'keyword' in cache['CC-MAIN-9999-99']['*.com']
        assert cache['CC-MAIN-9999-99']['*.com']['keyword'] == 2

    # Check that batch file exists
    batch_csv_data = CSVData(
        f"{temp_dir}/batch_info.csv"
    )
    # Check headers
    assert batch_csv_data.headers == BATCH_HEADERS
    # Check first row
    row_dict = batch_csv_data.rows[0]
    assert row_dict['Count'] == '1'
    assert row_dict['Datetime'] == '2022-12-12 12:00:00'
    assert row_dict['Keywords'] == '*.com - keyword'
    assert batch_csv_data.rows[0]['Source'] == 'Common Crawl'
    assert batch_csv_data.rows[0]['Notes'] == 'CC-MAIN-9999-99'

    # Run main again with different arguments and no reset_cache enabled, to test persistence of cache and output files
    mock_upload_file.side_effect = validate_csvs
    mock_args.reset_cache = False
    mock_args.common_crawl_id = 'CC-MAIN-0000-00'
    mock_args.url = '*.gov'
    mock_args.keyword = 'police'
    mock_args.pages = 3
    # output_filename, cache_filename, and data_dir are unchanged
    common_crawler_results_2 = [
        # This result, containing the search keyword should be returned in the final output
        [{
            'url': 'http://police.com'
        }],
        # This result, because it does not contain the keyword, should not
        [{
            'url': 'http://military.com'
        }],
        # This result, because it does contain the keyword, should be returned in the final output
        [{
            'url': 'http://police.com/page2'
        }]
    ]
    mock_search_cc_index.side_effect = common_crawler_results_2


    # Call main with test arguments
    main()

    # Check that the cache file was created, and contains the expected data
    with open(f'{temp_dir}/test_cache.json', 'r') as file:
        cache = json.load(file)
        # Check the original data persists
        assert 'CC-MAIN-9999-99' in cache
        assert '*.com' in cache['CC-MAIN-9999-99']
        assert 'keyword' in cache['CC-MAIN-9999-99']['*.com']
        assert cache['CC-MAIN-9999-99']['*.com']['keyword'] == 2
        # Check the new data exists as well
        assert 'CC-MAIN-0000-00' in cache
        assert '*.gov' in cache['CC-MAIN-0000-00']
        assert 'police' in cache['CC-MAIN-0000-00']['*.gov']
        assert cache['CC-MAIN-0000-00']['*.gov']['police'] == 3

    # Check that batch file exists
    batch_csv_data = CSVData(
        f"{temp_dir}/batch_info.csv"
    )
    # Check headers
    assert batch_csv_data.headers == BATCH_HEADERS
    # Check second row
    row_dict = batch_csv_data.rows[1]
    assert row_dict['Count'] == '2'
    assert row_dict['Datetime'] == '2022-12-12 12:00:00'
    assert row_dict['Keywords'] == '*.gov - police'
    assert row_dict['Source'] == 'Common Crawl'
    assert row_dict['Notes'] == 'CC-MAIN-0000-00'

@pytest.fixture
def temp_dir():
    dirpath = tempfile.mkdtemp()
    try:
        yield dirpath
    finally:
        shutil.rmtree(dirpath)


def test_csv_manager(temp_dir):
    """
    Confirm functionality of CSV manager, including:
        That headers are properly defined
        That rows are properly added
        That CSV Manager properly either creates a file or appends to a file if it already exists
    Returns:
    """
    temp_file = 'temp_file'
    headers = ['header1', 'header2', 'header3']
    csv_manager = CSVManager(
        file_name=temp_file,
        headers=headers,
        directory=temp_dir
    )
    # Add 2 rows of data
    rows = [
        ['data1', 'data2', 'data3'],
        ['data4', 'data5', 'data6']
    ]
    csv_manager.add_rows(rows)

    # Check file has two rows not including header
    temp_file_path = csv_manager.file_path
    csv_data = CSVData(temp_file_path)
    assert csv_data.headers == headers, "CSV file does not contain the expected headers"
    assert len(csv_data.rows) == 2, "CSV file does not contain the expected number of rows"

    # Re-initialize CSVManager, add an additional row, and check that there are now three rows
    csv_manager = CSVManager(
        file_name=temp_file,
        headers=headers,
        directory=temp_dir
    )
    csv_manager.add_rows([['data7', 'data8', 'data9']])
    # Check file has three rows not including header
    csv_data = CSVData(temp_file_path)
    assert csv_data.headers == headers, "CSV file does not contain the expected headers"
    assert len(csv_data.rows) == 3, "CSV file does not contain the expected number of rows"
