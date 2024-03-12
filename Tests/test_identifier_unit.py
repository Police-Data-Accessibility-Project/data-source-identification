import tempfile
from unittest.mock import patch

import pytest
import requests_mock

from agency_identifier.identifier import *


@pytest.fixture
def mock_env(monkeypatch):
    monkeypatch.setenv("VUE_APP_PDAP_API_KEY", "test_api_key")


def test_get_page_data_success(mock_env):
    with requests_mock.Mocker() as m:
        m.get("https://data-sources.pdap.io/api/agencies/1", json={"data": "test_data"}, status_code=200)
        data = get_page_data(1)
        assert data == "test_data"


def test_get_page_data_failure(mock_env):
    with requests_mock.Mocker() as m:
        m.get("https://data-sources.pdap.io/api/agencies/1", status_code=404)
        with pytest.raises(Exception):
            get_page_data(1)


@pytest.mark.parametrize("url,expected", [
    ("http://www.example.com", "example.com"),
    ("https://example.com", "example.com"),
    ("example.com", "example.com"),
    ("www.example.com", "example.com"),
])
def test_parse_hostname(url, expected):
    assert parse_hostname(url) == expected


@pytest.mark.parametrize("url", [
    "http:///www.example.com",  # Invalid URL
    "://example.com",  # Missing scheme
])
def test_parse_hostname_failure(url):
    with pytest.raises(Exception):
        parse_hostname(url)


@pytest.mark.parametrize("url,expected", [
    ("http://www.example.com", "example.com/"),
    ("https://example.com", "example.com/"),
    ("http://example.com/path/to/page", "example.com/path/to/page/"),
    ("www.example.com", "example.com/"),
    ("example.com/", "example.com/"),
])
def test_remove_http(url, expected):
    assert remove_http(url) == expected


@pytest.fixture
def agencies_and_hostnames():
    return (
        [{"name": "Agency 1", "homepage_url": "https://agency1.com"}],
        ["agency1.com"]
    )


def test_match_agencies_found(agencies_and_hostnames):
    agencies, agency_hostnames = agencies_and_hostnames
    match = match_agencies(agencies, agency_hostnames, "http://www.agency1.com/page")
    assert match["status"] == "Match found"
    assert match["agency"]["name"] == "Agency 1"


def test_match_agencies_no_match(agencies_and_hostnames):
    agencies, agency_hostnames = agencies_and_hostnames
    match = match_agencies(agencies, agency_hostnames, "http://www.nonexistentagency.com")
    assert match["status"] == "No match found"
    assert match["agency"] == []

@pytest.fixture
def agencies_with_same_hostname():
    return (
        [
            {"name": "Agency 1", "homepage_url": "http://agency.com/path1"},
            {"name": "Agency 2", "homepage_url": "http://agency.com/path2"}
        ],
        ["agency.com", "agency.com"]
    )

def test_match_agencies_multiple_found(agencies_with_same_hostname):
    agencies, agency_hostnames = agencies_with_same_hostname
    # A URL that matches the first agency more closely
    match = match_agencies(agencies, agency_hostnames, "http://agency.com/path1/page")
    assert match["status"] == "Match found"
    assert match["agency"]["name"] == "Agency 1"

    # A URL that doesn't closely match either agency's homepage URL path
    contested_match = match_agencies(agencies, agency_hostnames, "http://agency.com/otherpath/page")
    assert contested_match["status"] == "Contested match"
    assert contested_match["agency"] == []

    # A URL that matches the second agency more closely
    match_second = match_agencies(agencies, agency_hostnames, "http://agency.com/path2/anotherpage")
    assert match_second["status"] == "Match found"
    assert match_second["agency"]["name"] == "Agency 2"

@patch('agency_identifier.identifier.get_page_data')
def test_get_agencies_data(mock_get_page_data, mock_env):
    # Mock get_page_data to return a dictionary on the first call and an empty dictionary on the second call
    mock_get_page_data.side_effect = [
        [{"name": "Agency 1", "homepage_url": "https://agency1.com", "id": "1"}],  # First page data
        []  # Indicates no more pages
    ]

    df = get_agencies_data()
    assert not df.is_empty()
    assert len(df) == 1
    assert df["name"][0] == "Agency 1"
    assert df["homepage_url"][0] == "https://agency1.com"


# Sample data to simulate what `match_urls_to_agencies_and_clean_data` might return
sample_agencies_data = polars.DataFrame({
    "url": ["http://agency1.com", "http://agency2.com", "http://nonexistentagency.com"],
    "homepage_url": ["http://agency1.com", "http://agency2.com", None],
    "hostname": ["agency1.com", "agency2.com", None],
})

# Sample input URLs DataFrame
sample_urls_df = polars.DataFrame({
    "url": ["http://agency1.com/page1", "http://agency2.com/page2", "http://nonexistentagency.com/page"]
})


@pytest.fixture
def mock_match_urls_to_agencies_and_clean_data():
    with patch('agency_identifier.identifier.match_urls_to_agencies_and_clean_data') as mock:
        mock.return_value = sample_agencies_data
        yield mock


def test_process_data(mock_match_urls_to_agencies_and_clean_data):
    processed_df = process_data(sample_urls_df)

    # Verify that the mock was called once with the sample_urls_df
    mock_match_urls_to_agencies_and_clean_data.assert_called_once_with(sample_urls_df)

    # Check that the processed DataFrame has filtered out the unmatched URLs
    assert len(processed_df) == 2  # Expecting only matched URLs to be present

    # Check if the 'hostname' column exists and has no null values in the result
    assert "hostname" in processed_df.columns
    assert processed_df.filter(polars.col("hostname").is_null()).height == 0

    # You might also want to check specific values if necessary
    assert processed_df["url"].to_list() == ["http://agency1.com", "http://agency2.com"]


# Sample data to simulate what `get_agencies_data` might return
sample_get_agencies_data = polars.DataFrame({
    "homepage_url": ["http://agency1.com", "http://agency2.com"],
    "name": ["Agency 1", "Agency 2"],
    "count_data_sources": [10, 15],
    "hostname": ["agency1.com", "agency2.com"],  # Assume this is added by the function
})


@pytest.fixture
def mock_get_agencies_data():
    with patch('agency_identifier.identifier.get_agencies_data') as mock:
        mock.return_value = sample_get_agencies_data
        yield mock


def test_match_urls_to_agencies_and_clean_data(mock_get_agencies_data):
    matched_df = match_urls_to_agencies_and_clean_data(sample_urls_df)

    # Verify that `get_agencies_data` was called
    mock_get_agencies_data.assert_called_once()

    # Verify the structure and content of the matched DataFrame
    # Expect that each URL is matched with the correct agency based on the hostname
    # Additionally, check for the addition of any new columns or transformations you apply
    assert "homepage_url" in matched_df.columns
    assert len(matched_df) == len(sample_urls_df)  # Ensure all URLs are processed

    # Verify that URLs are correctly matched or not matched to agencies
    # This assumes that the function annotates the DataFrame with match results
    assert matched_df.filter(polars.col("url") == "http://agency1.com/page1").select("name")["name"][0] == "Agency 1"
    assert matched_df.filter(polars.col("url") == "http://nonexistentagency.com/page").select("name")["name"][0] == ""


def test_read_data_success():
    # Create a temporary file with some CSV content
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
        tmp.write("column1,column2\nvalue1,value2")
        tmp_path = tmp.name

    # Attempt to read the file with read_data
    try:
        df = read_data(tmp_path)
        assert not df.is_empty()
        assert "column1" in df.columns
        assert df.shape == (1, 2)
    finally:
        # Clean up the temporary file
        os.remove(tmp_path)

def test_read_data_failure():
    # Test reading a non-existent file should raise an exception
    with pytest.raises(Exception):
        read_data("non_existent_file.csv")


def test_write_data_success():
    # Create a DataFrame to write
    df = polars.DataFrame({"column1": ["value1"], "column2": ["value2"]})

    # Use a temporary file to write the DataFrame
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
        tmp_path = tmp.name

    # Write the DataFrame and verify the file contents
    try:
        write_data(df, tmp_path)

        # Read back the file to verify contents
        with open(tmp_path, 'r') as f:
            content = f.read()
            assert "column1,column2" in content
            assert "value1,value2" in content
    finally:
        # Clean up the temporary file
        os.remove(tmp_path)


def test_write_data_failure(monkeypatch):
    # Simulate an error by patching the `write_csv` method to raise an exception
    with monkeypatch.context() as m:
        m.setattr(polars.DataFrame, "write_csv",
                  lambda self, file_path: (_ for _ in ()).throw(Exception("Mock write failure")))
        with pytest.raises(Exception) as exc_info:
            df = polars.DataFrame({"column1": ["value1"], "column2": ["value2"]})
            write_data(df, "path/to/non_writable_directory/file.csv")
        assert "Mock write failure" in str(exc_info.value)

@patch('agency_identifier.identifier.write_data')
@patch('agency_identifier.identifier.process_data')
@patch('agency_identifier.identifier.read_data')
def test_process_and_write_data_success(mock_read_data, mock_process_data, mock_write_data):
    # Setup mock return values
    mock_read_data.return_value = polars.DataFrame({"url": ["http://example.com"]})
    processed_df = polars.DataFrame({"url": ["http://example.com"], "processed": [True]})
    mock_process_data.return_value = processed_df

    # Call the function with mocked input and output file paths
    process_and_write_data("input_file.csv", "output_file.csv")

    # Verify that read_data and write_data were called correctly
    mock_read_data.assert_called_once_with("input_file.csv")
    mock_process_data.assert_called_once_with(mock_read_data.return_value)
    mock_write_data.assert_called_once_with(processed_df, "output_file.csv")

@pytest.mark.parametrize("side_effect,expected_exception", [
    (FileNotFoundError, FileNotFoundError),
    (PermissionError, PermissionError),
])
@patch('agency_identifier.identifier.write_data')
@patch('agency_identifier.identifier.process_data')
@patch('agency_identifier.identifier.read_data')
def test_process_and_write_data_failure(mock_read_data, mock_process_data, mock_write_data, side_effect, expected_exception):
    mock_read_data.side_effect = side_effect

    with pytest.raises(expected_exception):
        process_and_write_data("input_file.csv", "output_file.csv")