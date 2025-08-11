import json
import time
from http import HTTPStatus
from typing import Union
from urllib.parse import quote_plus

import aiohttp

from src.collectors.impl.common_crawler.utils import URLWithParameters

async def async_make_request(
        search_url: 'URLWithParameters'
) -> Union[aiohttp.ClientResponse, None]:
    """
    Makes the HTTP GET request to the given search URL using aiohttp.
    Return the response if successful, None if rate-limited or failed.
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(str(search_url)) as response:
                text = await response.text()
                if (
                    response.status == HTTPStatus.INTERNAL_SERVER_ERROR
                    and "SlowDown" in text
                ):
                    return None
                response.raise_for_status()
                # simulate requests.Response interface for downstream compatibility
                response.text_content = text  # custom attribute for downstream use
                response.status_code = response.status
                return response
    except aiohttp.ClientError as e:
        print(f"Failed to get records: {e}")
        return None


async def make_request(
        search_url: 'URLWithParameters'
) -> Union[aiohttp.ClientResponse, None]:
    """Synchronous wrapper around the async function."""
    return await async_make_request(search_url)


def process_response(response, url: str, page: int) -> Union[list[str], None]:
    """Processes the HTTP response and returns the parsed records if successful."""
    if response is None:
        return None

    if response.status_code == HTTPStatus.OK:
        records = response.text_content.strip().split("\n")
        print(f"Found {len(records)} records for {url} on page {page}")
        results = []
        for record in records:
            d = json.loads(record)
            results.append(d["url"])
        return results

    if "First Page is 0, Last Page is 0" in response.text_content:
        print("No records exist in index matching the url search term")
        return None

    print(f"Unexpected response: {response.status_code}")
    return None


async def get_common_crawl_search_results(
        search_url: 'URLWithParameters',
        query_url: str,
        page: int
) -> Union[list[str], None]:
    response = await make_request(search_url)
    return process_response(response, query_url, page)



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

    async def run(self):
        url_results = []
        for page in range(self.start_page, self.start_page + self.num_pages):
            urls = await self.search_common_crawl_index(query_url=self.url, page=page)

            # If records were found, filter them and add to results
            if not urls:
                yield f"No records found for {self.url} on page {page}"
                continue

            keyword_urls = self.get_urls_with_keyword(urls, self.keyword)
            url_results.extend(keyword_urls)

            yield f"Found {len(keyword_urls)} records for {self.url} on page {page}"
            # Wait 5 seconds before making the next request, to avoid overloading the server
            time.sleep(5)

        yield f"Found {len(url_results)} total records for {self.url}"
        self.url_results = url_results


    async def search_common_crawl_index(
        self, query_url: str, page: int = 0, max_retries: int = 20
    ) -> list[str] or None:
        """
        This method is used to search the Common Crawl index for a given URL and page number
        Args:
            query_url: a URL to search for
            page: the page number to search

        Returns: A list of records (dictionaries) containing the search results

        """
        encoded_url = quote_plus(query_url)
        search_url = URLWithParameters(self.root_url)
        search_url.add_parameter("url", encoded_url)
        search_url.add_parameter("output", "json")
        search_url.add_parameter("page", page)

        retries = 0
        delay = 1

        # put HTTP GET request in re-try loop in case of rate limiting. Once per second is nice enough per common crawl doc.
        while retries < max_retries:
            results = await get_common_crawl_search_results(
                search_url=search_url, query_url=query_url, page=page)
            if results is not None:
                return results

            retries += 1
            print(
                f"Rate limit exceeded. Retrying in {delay} second(s)... (Attempt {retries}/{max_retries})"
            )
            time.sleep(delay)

        print(f"Max retries exceeded. Failed to get records for {query_url} on page {page}.")
        return None

    @staticmethod
    def get_urls_with_keyword(urls: list[str], keyword) -> list[str]:
        """
        Returns a list of URLs that contain the given keyword
        """
        return [url for url in urls if keyword in url]
