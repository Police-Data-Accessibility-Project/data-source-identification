import pytest
import requests
import requests_mock

from AnnotationHelper.harvest_html import fetch_html, harvest_html
from AnnotationHelper.preprocess_and_load_urls import CsvDataSource, PrintDataTarget, preprocess_and_load_urls


def test_fetch_html_success():
    with requests_mock.Mocker() as m:
        m.get('http://example.com', text='Success HTML Content')
        assert fetch_html('http://example.com') == 'Success HTML Content'


def test_fetch_html_request_exception():
    with requests_mock.Mocker() as m:
        m.get('http://example.com', exc=requests.exceptions.RequestException)
        with pytest.raises(requests.exceptions.RequestException):
            fetch_html('http://example.com')


def test_harvest_html_success(monkeypatch):
    # Mock `fetch_html` to return a specific HTML content
    def mock_fetch_html(url):
        return f"HTML content for {url}"

    monkeypatch.setattr('AnnotationHelper.harvest_html.fetch_html', mock_fetch_html)

    urls = ['http://example1.com', 'http://example2.com']
    expected = {url: f"HTML content for {url}" for url in urls}
    assert harvest_html(urls) == expected


def test_csv_data_source_load_urls(tmpdir):
    # Create a temporary CSV file
    p = tmpdir.mkdir("sub").join("urls.csv")
    p.write("http://example1.com\nhttp://example2.com")

    data_source = CsvDataSource(str(p))
    assert data_source.load_urls() == ["http://example1.com", "http://example2.com"]


def test_print_data_target_upload_data(capfd):
    data_target = PrintDataTarget()
    data = {"http://example.com": "HTML content"}
    data_target.upload_data(data)

    captured = capfd.readouterr()
    assert "URL: http://example.com, HTML Content: 12 characters" in captured.out


import pytest

# Mock implementations
def mock_load_urls(self):
    return ['http://example.com']

def mock_harvest_html(urls):
    return {'http://example.com': 'Mocked HTML content'}

class MockDataTarget:
    def __init__(self):
        self.uploaded_data = None

    def upload_data(self, data):
        self.uploaded_data = data

@pytest.fixture
def mock_data_source(monkeypatch):
    monkeypatch.setattr('AnnotationHelper.preprocess_and_load_urls.CsvDataSource.load_urls', mock_load_urls)

@pytest.fixture
def mock_html_harvester(monkeypatch):
    monkeypatch.setattr('AnnotationHelper.preprocess_and_load_urls.harvest_html', mock_harvest_html)

def test_preprocess_and_load_urls_integration(mock_data_source, mock_html_harvester):
    # Mock the data source and target
    data_source = CsvDataSource('dummy_path')  # The path won't be used due to mocking
    data_target = MockDataTarget()

    preprocess_and_load_urls(data_source, data_target)

    # Assertions
    assert data_target.uploaded_data == {'http://example.com': 'Mocked HTML content'}, "The data target did not receive the expected data"