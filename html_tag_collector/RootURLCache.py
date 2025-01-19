import json
import os
import ssl
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from html_tag_collector.constants import USER_AGENT, REQUEST_HEADERS

DEBUG = False

class RootURLCache:
    def __init__(self, cache_file='url_cache.json'):
        self.cache_file = cache_file
        self.cache = self.load_cache()

    def load_cache(self):
        if not os.path.exists(self.cache_file):
            return {}
        with open(self.cache_file, 'r') as f:
            # Check if the file is empty
            content = f.read()
            if not content:
                # Return an empty dictionary if the file is empty
                return {}
            # If the file is not empty, return its JSON content
            return json.loads(content)

    def save_cache(self):
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f, indent=4)

    def get_title(self, url) -> str:
        if not url.startswith('http'):
            url = "https://" + url

        parsed_url = urlparse(url)
        root_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

        if root_url in self.cache:
            return self.cache[root_url]

        # TODO: Separate the logic in these two sections
        try:
            response = requests.get(root_url, headers=REQUEST_HEADERS, timeout=120)
        except (requests.exceptions.SSLError, ssl.SSLError):
            # This error is raised when the website uses a legacy SSL version, which is not supported by requests
            # Retry without SSL verification
            try:
                response = requests.get(root_url, headers=REQUEST_HEADERS, timeout=120, verify=False)
            except Exception as e:
                return self.handle_exception(e)
        except Exception as e:
            return self.handle_exception(e)

        # TODO: Separate logic in these two sections
        soup = BeautifulSoup(response.text, 'html.parser')
        try:
            title = soup.find('title').text
        except AttributeError:
            title = ""

        self.cache[root_url] = title
        self.save_cache()

        # Prevents most bs4 memory leaks
        if soup.html:
            soup.html.decompose()

        return title

    def handle_exception(self, e):
        if DEBUG:
            return f"Error retrieving title: {e}"
        else:
            return ""
