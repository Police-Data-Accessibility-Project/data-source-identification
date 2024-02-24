from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
import json
import os


class RootURLCache:
    def __init__(self, cache_file='url_cache.json'):
        self.cache_file = cache_file
        self.cache = self.load_cache()

    def load_cache(self):
        if os.path.exists(self.cache_file):
            with open(self.cache_file, 'r') as f:
                return json.load(f)
        return {}

    def save_cache(self):
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f, indent=4)

    def get_title(self, url):
        parsed_url = urlparse(url)
        root_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

        if root_url not in self.cache:
            try:
                response = requests.get(root_url)
                soup = BeautifulSoup(response.text, 'html.parser')
                title = soup.find('title').text
                self.cache[root_url] = title
                self.save_cache()
                return title
            except Exception as e:
                return f"Error retrieving title: {e}"
        return self.cache[root_url]
