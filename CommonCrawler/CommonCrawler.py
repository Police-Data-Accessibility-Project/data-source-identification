import boto3
# from warcio.archiveiterator import ArchiveIterator
import requests
import json
from urllib.parse import quote_plus

def get_unique_url_roots(urls):
    return list(set([url.split('/')[2] for url in urls]))

class URLWithParameters:
    """
    Appends parameters to a URL
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

# This class is used to interact with the Common Crawl Index Server
class CommonCrawler:
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
            print(f"Found {len(records)} records for {url}")
            return [json.loads(record) for record in records]
        else:
            return None

    @staticmethod
    def get_urls(records: list[dict]):
        return [record['url'] for record in records]

    @staticmethod
    def get_urls_with_keyword(records: list[dict], keyword):
        return [record['url'] for record in records if keyword in record['url']]


if __name__ == "__main__":
    cc = CommonCrawler()
    url_to_search = "*.gov"
    cc.get_number_of_pages(url_to_search)
    records = cc.search_cc_index(url_to_search)
    urls = cc.get_urls(records)
    unique_urls = get_unique_url_roots(urls)
    print(f"Found {len(unique_urls)} Unique URL Roots from {len(urls)} URLs")
    print(get_unique_url_roots(urls))
    keyword_urls = cc.get_urls_with_keyword(records, "police")
    print(f"Found {len(keyword_urls)} URLs with the keyword 'police'")
    print(keyword_urls)
    # pass

