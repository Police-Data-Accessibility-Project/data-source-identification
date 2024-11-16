import json

from util.miscellaneous_functions import get_file_path

"""
This module contains classes for managing a cache of Common Crawl search results
These classes include:
    - CommonCrawlerCache: a class for managing the cache logic of Common Crawl search results
"""


class CommonCrawlerCacheManager:
    """
    A class for managing the cache of Common Crawl search results.
    This class is responsible for adding, retrieving, and saving cache data.
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
        self.cache = self.load_or_create_cache()

    def upsert(self, index: str, url: str, keyword: str, last_page: int) -> None:
        """
        Updates the cache with the last page crawled for a given index, url, and keyword.
        Or adds a new cache object if it does not exist.
        Args:
            index: the index of the common crawl
            url: the url to search
            keyword: the search term to use
            last_page: the last page crawled
        Returns: None
        """
        if index not in self.cache:
            self.cache[index] = {}
        if url not in self.cache[index]:
            self.cache[index][url] = {}
        self.cache[index][url][keyword] = last_page

    def get(self, index, url, keyword) -> int:
        """
        Retrieves a page number from the cache.
        Args:
            index: the index of the common crawl
            url: the url to search
            keyword: the search term to use

        Returns: int - the last page crawled

        """
        if (
            index in self.cache
            and url in self.cache[index]
            and keyword in self.cache[index][url]
        ):
            return self.cache[index][url][keyword]
        # The cache object does not exist. Return 0 as the default value.
        return 0

    def load_or_create_cache(self) -> dict:
        """
        Loads the cache from the configured file path.
        If the file does not exist, an empty dictionary is returned.
        Returns: dict - the cache data
        """
        try:
            with open(self.file_path, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return {}

    def save_cache(self) -> None:
        """
        Converts the cache object into a JSON-serializable format and saves it to the configured file path.
        This method ensures the cache is stored in a readable and easily reloadable format, allowing for
        persistence of crawl data across sessions.
        """
        # Reformat cache data for JSON serialization
        with open(self.file_path, "w") as file:
            json.dump(self.cache, file, indent=4)

    def reset_cache(self) -> None:
        """
        Resets the cache to an empty state.
        """
        self.cache = {}
        print("Cache has been reset.")
