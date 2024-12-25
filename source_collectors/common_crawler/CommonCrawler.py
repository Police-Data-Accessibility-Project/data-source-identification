import json
import time
from http import HTTPStatus
from urllib.parse import quote_plus

import requests

from source_collectors.common_crawler.utils import URLWithParameters


class CommonCrawler:

    def __init__(
        self,
        url: str,
        keyword: str,
        start_page: int = 1,
        num_pages: int = 1,
        crawl_id: str = "CC-MAIN-2023-50",
    ):
        """
        Initializes the CommonCrawlerManager with a crawl ID.
        Args:
            crawl_id: the Common Crawl index to use
        """
        self.crawl_id = crawl_id
        CC_INDEX_SERVER = "http://index.commoncrawl.org/"
        INDEX_NAME = f"{self.crawl_id}-index"
        self.root_url = f"{CC_INDEX_SERVER}{INDEX_NAME}"

        self.url = url
        self.keyword = keyword
        self.start_page = start_page
        self.num_pages = num_pages
        self.url_results = None

    def run(self):
        url_results = []
        for page in range(self.start_page, self.start_page + self.num_pages):
            # Wait 5 seconds before making the next request, to avoid overloading the server
            time.sleep(5)
            records = self.search_common_crawl_index(url=self.url, page=page)

            # If records were found, filter them and add to results
            if not records:
                yield f"No records found for {self.url} on page {page}"
                continue

            keyword_urls = self.get_urls_with_keyword(records, self.keyword)
            url_results.extend(keyword_urls)

            yield f"Found {len(keyword_urls)} records for {self.url} on page {page}"

        yield f"Found {len(url_results)} total records for {self.url}"
        self.url_results = url_results


    def search_common_crawl_index(
        self, url: str, page: int = 0, max_retries: int = 20
    ) -> list[dict]:
        """
        This method is used to search the Common Crawl index for a given URL and page number
        Args:
            url: a URL to search for
            page: the page number to search

        Returns: A list of records (dictionaries) containing the search results

        """
        encoded_url = quote_plus(url)
        search_url = URLWithParameters(self.root_url)
        search_url.add_parameter("url", encoded_url)
        search_url.add_parameter("output", "json")
        search_url.add_parameter("page", page)

        retries = 0
        delay = 1

        # put HTTP GET request in re-try loop in case of rate limiting. Once per second is nice enough per common crawl doc.
        while retries < max_retries:
            response = self.make_request(search_url)
            if response:
                return self.process_response(response, url, page)

            retries += 1
            print(
                f"Rate limit exceeded. Retrying in {delay} second(s)... (Attempt {retries}/{max_retries})"
            )
            time.sleep(delay)

        print(f"Max retries exceeded. Failed to get records for {url} on page {page}.")
        return None

    def make_request(self, search_url: str) -> requests.Response:
        """
        Makes the HTTP GET request to the given search URL.
        Return the response if successful, None if rate-limited.
        """
        try:
            response = requests.get(str(search_url))
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            if (
                response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
                and "SlowDown" in response.text
            ):
                return None
            else:
                print(f"Failed to get records: {e}")
                return None

    def process_response(
        self, response: requests.Response, url: str, page: int
    ) -> list[dict]:
        """Processes the HTTP response and returns the parsed records if successful."""
        if response.status_code == HTTPStatus.OK:
            records = response.text.strip().split("\n")
            print(f"Found {len(records)} records for {url} on page {page}")
            return [json.loads(record) for record in records]
        elif "First Page is 0, Last Page is 0" in response.text:
            print("No records exist in index matching the url search term")
            return None
        else:
            print(f"Unexpected response: {response.status_code}")
            return None

    @staticmethod
    def get_urls_with_keyword(records: list[dict], keyword) -> list[str]:
        """
        Returns a list of URLs that contain the given keyword
        """
        return [record["url"] for record in records if keyword in record["url"]]
