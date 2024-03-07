import json

from common_crawler.utils import get_file_path

"""
This module contains classes for managing a cache of Common Crawl search results
"""


class CommonCrawlerCacheObject:
    """
    An object recording a single combination of an index, url, and search term
    Parameters:
        index: str - the index of the common crawl
        url: str - the url to search
        search_term: str - the search term to use
        last_page: int - the last page searched (0 if not searched yet)
    """

    def __init__(self, index: str, url: str, search_term: str, last_page: int = 0):
        self.index = index
        self.url = url
        self.search_term = search_term
        self.last_page = last_page

    def get_next_page(self):
        self.last_page += 1
        return self.last_page

    def __str__(self):
        return f"Index: {self.index}, URL: {self.url}, Search Term: {self.search_term}, Page Count: {self.last_page}"

    def to_dict(self):
        return {
            'index': self.index,
            'url': self.url,
            'search_term': self.search_term,
            'count': self.last_page
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data['index'], data['url'], data['search_term'], data['count'])


class CacheStorage:
    def __init__(self, file_name: str = "cache", directory=None):
        self.file_path = get_file_path(f"{file_name}.json", directory)
        print(f"Cache file path: {self.file_path}")

    def load_cache(self):
        try:
            with open(self.file_path, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            return {}

    def save_cache(self, cache):
        readable_cache = {}
        for index, index_data in cache.items():
            readable_cache[index] = {}
            for url, url_data in index_data.items():
                readable_cache[index][url] = {}
                for search_term, cache_object in url_data.items():
                    readable_cache[index][url][search_term] = {
                        'last_page_crawled': cache_object.last_page
                    }
        with open(self.file_path, 'w') as file:
            json.dump(readable_cache, file, indent=4)


class CommonCrawlerCacheManager:
    def __init__(self, storage: CacheStorage):
        self.storage = storage
        self.cache = self.load_or_create_cache()

    def add(self, index, url, search_term):
        if index not in self.cache:
            self.cache[index] = {}
        if url not in self.cache[index]:
            self.cache[index][url] = {}
        self.cache[index][url][search_term] = CommonCrawlerCacheObject(index, url, search_term)

    def get(self, index, url, search_term):
        if index in self.cache and url in self.cache[index] and search_term in self.cache[index][url]:
            return self.cache[index][url][search_term]
        else:
            self.add(index, url, search_term)
            return self.cache[index][url][search_term]

    def load_or_create_cache(self):
        data = self.storage.load_cache()
        cache = {}
        for index, index_data in data.items():
            cache[index] = {}
            for url, url_data in index_data.items():
                cache[index][url] = {}
                for search_term, cache_data in url_data.items():
                    last_page_crawled = cache_data['last_page_crawled']
                    cache_object = CommonCrawlerCacheObject(index, url, search_term, last_page_crawled)
                    cache[index][url][search_term] = cache_object
        return cache

    def save_cache(self):
        self.storage.save_cache(self.cache)
