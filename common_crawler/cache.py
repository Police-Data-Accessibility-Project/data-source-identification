import json

from common_crawler.utils import get_file_path

"""
This module contains classes for managing a cache of Common Crawl search results
These classes include:
    - CommonCrawlerCacheObject: stores the cache data. Represents a single combination of an index, url, and search term
    - CacheStorage: a class for managing the persistence layer (storage of the cache data)
    - CommonCrawlerCacheManager: a class for managing the cache logic of Common Crawl search results
"""


class CommonCrawlerCacheObject:
    """
    An object recording a single combination of an index, url, and search term
    Parameters:
        index: str - the index of the common crawl
        url: str - the url to search
        keyword: str - the search term to use
        last_page: int - the last page searched (0 if not searched yet)
    """

    def __init__(self, index: str, url: str, keyword: str, last_page: int = 0):
        self.index = index
        self.url = url
        self.keyword = keyword
        self.last_page = last_page

    def __str__(self):
        return f"Index: {self.index}, URL: {self.url}, Search Term: {self.keyword}, Page Count: {self.last_page}"

    def to_dict(self):
        return {
            'index': self.index,
            'url': self.url,
            'keyword': self.keyword,
            'count': self.last_page
        }


class CacheStorage:
    """
    A class for managing the storage of the cache data.
    This class is responsible for loading and saving the cache to a file.
    """
    def __init__(self, file_name: str = "cache", directory=None):
        """
        Initializes the CacheStorage object with a file name and directory.
        Args:
            file_name: the name of the cache file
            directory: the directory to store the cache file
        """
        self.file_path = get_file_path(f"{file_name}.json", directory)
        print(f"Cache file path: {self.file_path}")

    def load_cache(self):
        """
        Loads the cache from the configured file path.
        If the file does not exist, an empty dictionary is returned.
        Returns: dict - the cache data
        """
        try:
            with open(self.file_path, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            return {}

    def save_cache(self, cache):
        """
        Converts the cache object into a JSON-serializable format and saves it to the configured file path.
        This method ensures the cache is stored in a readable and easily reloadable format, allowing for
        persistence of crawl data across sessions.
        """
        # Reformat cache data for JSON serialization
        readable_cache = {}
        for index, index_data in cache.items():
            readable_cache[index] = {}
            for url, url_data in index_data.items():
                readable_cache[index][url] = {}
                for keyword, cache_object in url_data.items():
                    # Save only essential information to minimize file size
                    readable_cache[index][url][keyword] = {
                        'last_page_crawled': cache_object.last_page
                    }
        with open(self.file_path, 'w') as file:
            json.dump(readable_cache, file, indent=4)


class CommonCrawlerCacheManager:
    """
    A class for managing the cache of Common Crawl search results.
    This class is responsible for adding, retrieving, and saving cache data.
    """
    def __init__(self, storage: CacheStorage):
        """
        Initializes the CommonCrawlerCacheManager with a CacheStorage object.
        Args:
            storage: the CacheStorage object to use for loading and saving the cache
        """
        self.storage = storage
        self.cache = self.load_or_create_cache()

    def add(self, index, url, keyword) -> None:
        """
        Adds a new cache object to the cache.
        Args:
            index: the index of the common crawl
            url: the url to search
            keyword: the search term to use
        """
        if index not in self.cache:
            self.cache[index] = {}
        if url not in self.cache[index]:
            self.cache[index][url] = {}
        self.cache[index][url][keyword] = CommonCrawlerCacheObject(index, url, keyword)

    def get(self, index, url, keyword) -> CommonCrawlerCacheObject:
        """
        Retrieves a cache object from the cache.
        Args:
            index: the index of the common crawl
            url: the url to search
            keyword: the search term to use

        Returns: CommonCrawlerCacheObject - the cache object

        """
        if index in self.cache and url in self.cache[index] and keyword in self.cache[index][url]:
            return self.cache[index][url][keyword]
        else:
            self.add(index, url, keyword)
            return self.cache[index][url][keyword]

    def load_or_create_cache(self) -> dict:
        """
        Loads the cache from storage if it exists, or creates a new cache if it does not.
        Returns: dict - the cache data
        """
        data = self.storage.load_cache()
        cache = {}
        for index, index_data in data.items():
            cache[index] = {}
            for url, url_data in index_data.items():
                cache[index][url] = {}
                for keyword, cache_data in url_data.items():
                    last_page_crawled = cache_data['last_page_crawled']
                    cache_object = CommonCrawlerCacheObject(index, url, keyword, last_page_crawled)
                    cache[index][url][keyword] = cache_object
        return cache

    def save_cache(self) -> None:
        """
        Saves the cache to storage.
        """
        self.storage.save_cache(self.cache)

    def reset_cache(self) -> None:
        """
        Resets the cache to an empty state.
        """
        self.cache = {}
        print("Cache has been reset.")
