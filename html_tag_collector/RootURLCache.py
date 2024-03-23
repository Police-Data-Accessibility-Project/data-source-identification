from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
import json
import os
import ssl


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
        if not url.startswith('http'):
            url = "https://" + url

        parsed_url = urlparse(url)
        root_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        headers = {
            # Some websites refuse the connection of automated requests, setting the User-Agent will circumvent that
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
        }

        if root_url not in self.cache:
            try:
                response = requests.get(root_url, headers=headers)
            except (requests.exceptions.SSLError, ssl.SSLError):
                # This error is raised when the website uses a legacy SSL version, which is not supported by requests
                # Retry without SSL verification
                try:
                    response = requests.get(url, headers=headers, verify=False)
                except Exception as e:
                    return f"Error retrieving title: {e}"
            except Exception as e:
                return f"Error retrieving title: {e}"

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

        return self.cache[root_url]
