# test_script_name.py
import pytest
from html_tag_collector.collector import parse_response  # Adjust the import according to your script's structure
from unittest.mock import Mock, patch

# Additional setup for testing, such as fixture definitions, could go here

def test_parse_response_success():
    # Mocking a successful response object
    response_mock = Mock()
    response_mock.status_code = 200
    response_mock.ok = True
    response_mock.html.html = '<html><head><title>Test Title</title><meta name="description" content="Test Description"></meta></head></html>'

    url_response = {
        "response": response_mock,
        "index": 1,
        "url": ["https://example.com", ]
    }

    with patch('html_tag_collector.collector.root_url_cache.get_title', return_value="Mocked Root Page Title") as mock_get_title:
        result = parse_response(url_response)

    # Verify the returned structure
    assert result["http_response"] == 200
    assert result["html_title"] == "Test Title"
    assert result["root_page_title"] == "Mocked Root Page Title"
    assert result["meta_description"] == "Test Description"
    # Ensure your mock was called as expected
    mock_get_title.assert_called_once_with("https://example.com")

def test_parse_response_res_is_none():
    url_response = {
        "response": None,  # Simulating a failed request
        "index": 1,
        "url": ["https://example.com", ]
    }

    # No need to mock `get_title` since it shouldn't be called when res is None
    result = parse_response(url_response)

    # Verify the function handles a None response correctly
    assert result["http_response"] == -1
    # Additional assertions can be made based on your implementation's expected behavior


def test_parse_response_res_not_ok():
    # Mocking an unsuccessful response object
    response_mock = Mock()
    response_mock.ok = False
    response_mock.status_code = 404  # Simulating a 404 Not Found response

    url_response = {
        "response": response_mock,
        "index": 1,
        "url": "https://example.com"
    }

    with patch('html_tag_collector.collector.root_url_cache.get_title', return_value="Mocked Root Page Title") as mock_get_title:
        result = parse_response(url_response)

    # Verify the function handles an unsuccessful response correctly
    assert result["http_response"] == 404
    # `get_title` should not be called since the response was not OK
    mock_get_title.assert_not_called()
    # Additional assertions can be made based on your implementation's expected behavior
