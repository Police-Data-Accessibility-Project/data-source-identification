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
                # Check if the file is empty
                content = f.read()
                if not content:
                    # Return an empty dictionary if the file is empty
                    return {}
                # If the file is not empty, return its JSON content
                return json.loads(content)
        return {}

    def save_cache(self):
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f, indent=4)

    def get_title(self, url):
        parsed_url = urlparse(url)
        root_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        headers = {
            # Some websites refuse the connection of automated requests, setting the User-Agent will circumvent that
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
        }

        if root_url not in self.cache:
            try:
                print(root_url)
                response = requests.get(root_url, headers=headers)
                soup = BeautifulSoup(response.text, 'html.parser')
                title = soup.find('title').text
                self.cache[root_url] = title
                self.save_cache()
                return title
            except Exception as e:
                return f"Error retrieving title: {e}"
        return self.cache[root_url]
