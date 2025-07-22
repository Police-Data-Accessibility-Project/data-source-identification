import csv
import datetime
import json
import os
import shutil
import tempfile
from unittest.mock import patch

import pytest
from common_crawler.cache import CommonCrawlerCacheManager
from common_crawler.csv_manager import CSVManager
from common_crawler.main import main, BATCH_HEADERS


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
