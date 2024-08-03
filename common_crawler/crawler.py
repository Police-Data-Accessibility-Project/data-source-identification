import json
import time
from urllib.parse import quote_plus
from http import HTTPStatus

import requests

from .utils import URLWithParameters
from dataclasses import dataclass
from collections import namedtuple

"""
This module contains classes for managing a cache of Common Crawl search results
"""

# TODO: What happens when no results are found? How does the CommonCrawlerManager handle this?



@dataclass
class CommonCrawlResult:
    last_page_search: int
    url_results: list[str]


class CommonCrawlerManager:
    """
    This class orchestrates the crawling process, leveraging CommonCrawler for
    actual interactions with the Common Crawl Index Server and CommonCrawlerCacheManager
    for caching results.
    It validates crawl ids, manages pagination, and aggregates results.
    """

    def __init__(self, crawl_id='CC-MAIN-2023-50'):
        self.crawl_id = crawl_id
        CC_INDEX_SERVER = 'http://index.commoncrawl.org/'
        INDEX_NAME = f'{self.crawl_id}-index'
        self.root_url = f'{CC_INDEX_SERVER}{INDEX_NAME}'

    def crawl(self, search_term, keyword, start_page, num_pages) -> CommonCrawlResult:
        print(
            f"Searching for {keyword} on {search_term} in {self.crawl_id} for {num_pages} pages,"
            f" starting at page {start_page}")

        url_results = []

        end_page = start_page + num_pages
        last_page = start_page

        for next_page in range(start_page, end_page):
            records = self.search_common_crawl_index(search_term, next_page)

            # If records were found, filter them and add to results
            if not records:
                continue

            keyword_urls = self.get_urls_with_keyword(records, keyword)
            url_results.extend(keyword_urls)

            last_page = next_page

            # Wait 5 seconds before making the next request, to avoid overloading the server
            time.sleep(5)

        return CommonCrawlResult(last_page, url_results)

    def search_common_crawl_index(self, url: str, page: int = 0, max_retries: int = 20) -> list[dict]:
        """
        This method is used to search the Common Crawl index for a given URL and page number
        Args:
            url: a URL to search for
            page: the page number to search

        Returns: A list of records (dictionaries) containing the search results

        """
        encoded_url = quote_plus(url)
        search_url = URLWithParameters(self.root_url)
        search_url.add_parameter('url', encoded_url)
        search_url.add_parameter('output', 'json')
        search_url.add_parameter('page', page)

        retries = 0
        delay = 1

        # put HTTP GET request in re-try loop in case of rate limiting. Once per second is nice enough per common crawl doc.
        while retries < max_retries:
            response = self.make_request(search_url)
            if response:
                return self.process_response(response, url, page)

            retries += 1
            print(f"Rate limit exceeded. Retrying in {delay} second(s)... (Attempt {retries}/{max_retries})")
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
            if response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR and 'SlowDown' in response.text:
                return None
            else:
                print(f"Failed to get records: {e}")
                return None

    def process_response(self, response: requests.Response, url: str, page: int) -> list[dict]:
        """Processes the HTTP response and returns the parsed records if successful."""
        if response.status_code == HTTPStatus.OK:
            records = response.text.strip().split('\n')
            print(f"Found {len(records)} records for {url} on page {page}")
            return [json.loads(record) for record in records]
        elif 'First Page is 0, Last Page is 0' in response.text:
            print("No records exist in index matching the url search term")
            return None
        else:
            print(f"Unexpected response: {response.status_code}")
            return None

    @staticmethod
    def get_urls_with_keyword(records: list[dict], keyword) -> list[str]:
        return [record['url'] for record in records if keyword in record['url']]
