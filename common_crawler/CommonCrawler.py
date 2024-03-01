import argparse
import os
import re

import requests
import json
from urllib.parse import quote_plus

def get_unique_url_roots(urls):
    return list(set([url.split('/')[2] for url in urls]))


class CommonCrawlerCacheObject:
    """
    An object recording a single combination of an index, url, and search term
    Parameters:
        index: str - the index of the common crawl
        url: str - the url to search
        search_term: str - the search term to use
        page_count: int - the last page searched (0 if not searched yet)
    """
    def __init__(self, index: str, url: str, search_term: str, page_count: int = 0):
        self.index = index
        self.url = url
        self.search_term = search_term
        self.count = page_count

    def get_next_page(self):
        self.count += 1
        return self.count

    def __str__(self):
        return f"Index: {self.index}, URL: {self.url}, Search Term: {self.search_term}, Page Count: {self.count}"

    def to_dict(self):
        return {
            'index': self.index,
            'url': self.url,
            'search_term': self.search_term,
            'count': self.count
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data['index'], data['url'], data['search_term'], data['count'])

class CommonCrawlerCache:
    """
    Acts as a centralized cache to manage CommonCrawlerCacheObjects
    Utilizes nested dictionaries for lookups and provides methods to add, retrieve, and save cache objects
    """
    def __init__(self):
        self.cache = {}

    def add(self, index: str, url: str, search_term: str):
        """
        Add a new search to the cache
        Args:
            index:
            url:
            search_term:
        Returns:

        """
        if index not in self.cache:
            self.cache[index] = {}
        if url not in self.cache[index]:
            self.cache[index][url] = {}
        self.cache[index][url][search_term] = CommonCrawlerCacheObject(index, url, search_term)


    def get(self, index: str, url: str, search_term: str):
        """
        Retrieves an existing Cache Object if it exists, or else creates it
        Args:
            index:
            url:
            search_term:

        Returns:

        """
        if index in self.cache and url in self.cache[index] and search_term in self.cache[index][url]:
            return self.cache[index][url][search_term]
        else:
            self.add(index, url, search_term)
            return self.cache[index][url][search_term]

    def get_cache_file_path(self):
        # Get the directory where the script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # Specify the name or relative path of your file from the script location
        file_name = "cache.json"

        # Construct the full path to the file
        file_path = os.path.join(script_dir, file_name)
        return file_path



    def save_cache(self):
        file_path = self.get_cache_file_path()
        with open(file_path, 'w') as file:
            # Save the last page crawled instead of the CommonCrawlerCacheObject
            readable_cache = {}
            for index, index_data in self.cache.items():
                readable_cache[index] = {}
                for url, url_data in index_data.items():
                    readable_cache[index][url] = {}
                    for search_term, cache_object in url_data.items():
                        readable_cache[index][url][search_term] = {
                            'last_page_crawled': cache_object.count
                        }
            json.dump(readable_cache, file, indent=4)


    def load_or_create_cache(self):
        file_path = self.get_cache_file_path()
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
                self.cache = {}
                for index, index_data in data.items():
                    self.cache[index] = {}
                    for url, url_data in index_data.items():
                        self.cache[index][url] = {}
                        for search_term, cache_data in url_data.items():
                            last_page_crawled = cache_data['last_page_crawled']
                            cache_object = CommonCrawlerCacheObject(index, url, search_term, last_page_crawled)
                            self.cache[index][url][search_term] = cache_object
        except FileNotFoundError:
            self.cache = {}

    def __str__(self):
        return str(self.cache)




class URLWithParameters:
    """
    A class to handle URLs with parameters, allowing for easy addition of parameters
    """
    def __init__(self, url):
        self.url = url

    def add_parameter(self, parameter, value):
        if '?' in self.url:
            self.url += f"&{parameter}={value}"
        else:
            self.url += f"?{parameter}={value}"
        return self.url

    def __str__(self):
        return self.url


class CommonCrawlerManager:
    """
    This class orchestrates the crawling process, leveraging CommonCrawler for
    actual interactions with the Common Crawl Index Server and CommonCrawlerCache
    for caching results.
    It validates crawl ids, manages pagination, and aggregates results.
    """
    def __init__(self):
        self.cache = CommonCrawlerCache()

    def reset_cache(self):
        # Reset the cache
        self.cache.cache = {}  # Assuming your cache data is stored in a dictionary attribute called 'cache'
        print("Cache has been reset.")

    def crawl(self, crawl_id, url, search_term, num_pages):

        # Check that crawl_id is valid
        if not re.match(r'CC-MAIN-\d{4}-\d{2}', crawl_id):
            raise ValueError("Invalid crawl_id")

        print(f"Searching for {search_term} on {url} in {crawl_id} for {num_pages} pages")

        # Create Common Crawler
        cc = CommonCrawler(crawl_id)

        # Initialize results list
        results = []

        # Loop over the number of pages
        for _ in range(num_pages):
            # Retrieve the cache object
            cache_object = self.cache.get(crawl_id, url, search_term)

            # Get the next page to search
            next_page = cache_object.get_next_page()

            # Search the Common Crawl index
            records = cc.search_cc_index(url, next_page)

            # If records were found, filter them and add to results
            if records:
                keyword_urls = cc.get_urls_with_keyword(records, search_term)
                results.extend(keyword_urls)

        # Save cache
        self.cache.save_cache()

        return results

# This class is used to interact with the Common Crawl Index Server
class CommonCrawler:
    """
    This class is used to interact directly with the Common Crawl Index Server,
    encapsulating the logic for making HTTP requests, handling pagination, and extracting data from the responses.
    """
    def __init__(self, crawl_id='CC-MAIN-2023-50'):
        self.CC_INDEX_SERVER = 'http://index.commoncrawl.org/'
        self.INDEX_NAME = f'{crawl_id}-index'
        self.root_url = f'{self.CC_INDEX_SERVER}{self.INDEX_NAME}'


    def get_number_of_pages(self, url):
        """
        This method is used to get the number of pages in the Common Crawl index for a given URL
         along with an estimate of the total number of records (assuming 15,000 records per page)
        Args:
            url: URL to query off of


        """
        encoded_url = quote_plus(url)
        search_url = URLWithParameters(self.root_url)
        search_url.add_parameter('url', encoded_url)
        search_url.add_parameter('output', 'json')
        search_url.add_parameter('showNumPages', 'true')
        response = requests.get(str(search_url))
        if response.status_code == 200:
            json_response = json.loads(response.text.strip())
            print(f"Found {json_response['pages']} pages for {url}")
            # Estimate also the total number of records
            total_records = json_response['pages'] * 15000
            print(f"Estimated {total_records} records for {url}")
        else:
            print(f"Failed to get number of pages for {url}")


    def search_cc_index(self, url, page=0):
        encoded_url = quote_plus(url)
        search_url = URLWithParameters(self.root_url)
        search_url.add_parameter('url', encoded_url)
        search_url.add_parameter('output', 'json')
        search_url.add_parameter('page', page)
        response = requests.get(str(search_url))
        # print("Response from CCI:", response.text)  # Output the response from the server
        if response.status_code == 200:
            records = response.text.strip().split('\n')
            print(f"Found {len(records)} records for {url} on page {page}")
            return [json.loads(record) for record in records]
        else:
            return None

    @staticmethod
    def get_urls(records: list[dict]):
        return [record['url'] for record in records]

    @staticmethod
    def get_urls_with_keyword(records: list[dict], keyword):
        return [record['url'] for record in records if keyword in record['url']]


def main():
    # Create the parser
    parser = argparse.ArgumentParser(
        description='Query the Common Crawl dataset and optionally save the results to a file.')

    # Add the required arguments
    parser.add_argument('common_crawl_id', type=str, help='The Common Crawl ID')
    parser.add_argument('url', type=str, help='The URL to query')
    parser.add_argument('search_term', type=str, help='The search term')

    # Optional arguments for the number of pages and the output file, and a flag to reset the cache
    parser.add_argument('-p', '--pages', type=int, default=1, help='The number of pages to search (default: 1)')
    parser.add_argument('-o', '--output', type=str, help='The name of the output text file for the URLs (optional)')
    parser.add_argument('--reset-cache', action='store_true', help='Reset the cache before starting the crawl')

    # Parse the arguments
    args = parser.parse_args()

    # Initialize the CommonCrawlerManager
    manager = CommonCrawlerManager()

    if args.reset_cache:
        manager.reset_cache()

    try:
        # Use the parsed arguments
        results = manager.crawl(args.common_crawl_id, args.url, args.search_term, args.pages)

        # Process the results
        if results:
            if args.output:
                # If an output file is specified, write the URLs to the file
                with open(args.output, 'w') as f:
                    for result in results:
                        f.write(result + '\n')
                print(f"URLs written to {args.output}")
            else:
                # If no output file is specified, print the URLs to the console
                print("Found URLs:")
                for result in results:
                    print(result)
        else:
            print("No results found.")
    except ValueError as e:
        print(f"Error during crawling: {e}")
    except Exception as e:
        # Catch-all for any other errors
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    # Example usage: python CommonCrawler.py CC-MAIN-2023-50 *.gov "police"
    # Usage with optional arguments: python CommonCrawler.py CC-MAIN-2023-50 *.gov "police" -p 2 -o police_urls.txt
    main()