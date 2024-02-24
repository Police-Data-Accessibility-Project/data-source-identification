import pytest
import responses
import json
import polars as pl
from html_tag_collector.collector import process_in_batches  # Adjust this import to your script structure

# Mocking HTTP responses for our test URLs
test_urls = [
    {
        "url": "https://example.com",
        "headers": {"Content-Type": "text/html"},
        "body": "<html><head><title>Example Title</title><meta name='description' content='Example Description'></head><body><h1>Example Heading</h1></body></html>",
        "status": 200
    },
    # Add more test cases as needed
]

# Expected results for verification
expected_data = [
    {
        "url": "https://example.com",
        "html_title": "Example Title",
        "meta_description": "Example Description",
        "h1": '["Example Heading"]'
    },
    # Match the structure to your expected output, based on the test_urls
]

@pytest.fixture
def setup_responses():
    with responses.RequestsMock() as rsps:
        for test_url in test_urls:
            rsps.add(responses.GET, test_url["url"], body=test_url["body"], status=test_url["status"], content_type=test_url["headers"]["Content-Type"])
        yield

def test_process_in_batches(setup_responses):
    # Convert test URLs to the required input format
    input_data = [{"url": url["url"]} for url in test_urls]
    df = pl.DataFrame(input_data)

    # Call the process_in_batches function with our test dataframe
    result_df = process_in_batches(df, batch_size=1)  # Using a small batch size for testing

    # Convert result_df to a list of dicts for easier comparison
    result_list = result_df.to_dicts()

    # Verify the output
    for expected, result in zip(expected_data, result_list):
        assert result["url"] == expected["url"]
        assert result["html_title"] == expected["html_title"]
        assert result["meta_description"] == expected["meta_description"]
        assert json.loads(result["h1"]) == json.loads(expected["h1"])

def test_process_in_batches_real_world_data():
    url = 'https://books.toscrape.com/catalogue/i-had-a-nice-time-and-other-lies-how-to-find-love-sht-like-that_814/index.html'
    df = pl.DataFrame([{"url": url}])
    result_df = process_in_batches(df, batch_size=1)
    result_dict = result_df.to_dict()
    assert result_dict["url"][0] == url
    assert result_dict["html_title"][0].strip() == "I Had a Nice Time And Other Lies...: How to find love & sh*t like that | Books to Scrape - Sandbox"
    assert result_dict["root_page_title"][0].strip() == "All products | Books to Scrape - Sandbox"
    assert 'The New York Times bestselling authors of Nice Is Just a Place in France' in result_dict["meta_description"][0]
    # assert result_dict["html_title"] == "All products | Books to Scrape - Sandbox"
