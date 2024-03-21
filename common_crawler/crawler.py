import json
import time
from urllib.parse import quote_plus

import requests

from .utils import URLWithParameters
from dataclasses import dataclass
from collections import namedtuple

"""
This module contains classes for managing a cache of Common Crawl search results
"""

# TODO: What happens when no results are found? How does the CommonCrawlerManager handle this?

# A named tuple for results
UrlResults = namedtuple(
    typename='UrlResults',
    field_names=['index', 'search_term', 'keyword', 'page', 'url']
)


@dataclass
class CommonCrawlResult:
    last_page_search: int
    url_results: list[UrlResults]


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

        url_results: list[UrlResults] = []

        end_page = start_page + num_pages
        last_page = start_page

        for next_page in range(start_page, end_page):
            records = self.search_common_crawl_index(search_term, next_page)

            # If records were found, filter them and add to results
            if not records:
                continue

            keyword_urls = self.get_urls_with_keyword(records, keyword)
            for keyword_url in keyword_urls:
                url_results.append(
                    UrlResults(
                        index=self.crawl_id,
                        url=keyword_url,
                        search_term=search_term,
                        page=next_page,
                        keyword=keyword))

            last_page = next_page

            # Wait 5 seconds before making the next request, to avoid overloading the server
            time.sleep(5)

        return CommonCrawlResult(last_page, url_results)

    def search_common_crawl_index(self, url: str, page: int = 0) -> list[dict]:
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

        # Perform an HTTP GET request to retrieve records for the encoded URL.
        response = requests.get(str(search_url))

        # If the request is successful, parse each record from the response and return them.
        if response.status_code == 200:
            records = response.text.strip().split('\n')
            print(f"Found {len(records)} records for {url} on page {page}")
            return [json.loads(record) for record in records]
        elif 'First Page is 0, Last Page is 0' in response.text:
            print("No records exist in index matching the url search term")
            return None
        else:
            print(f"Failed to get records for {url} on page {page}: {response.text}")
            # Return None to indicate that no records were found or an error occurred.
            return None

    @staticmethod
    def get_urls_with_keyword(records: list[dict], keyword) -> list[str]:
        return [record['url'] for record in records if keyword in record['url']]
