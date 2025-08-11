from typing import Optional
from urllib.parse import urlparse

from aiohttp import ClientSession
from bs4 import BeautifulSoup

from src.db.client.async_ import AsyncDatabaseClient
from src.core.tasks.url.operators.html.scraper.root_url_cache.constants import REQUEST_HEADERS
from src.core.tasks.url.operators.html.scraper.root_url_cache.dtos.response import RootURLCacheResponseInfo

DEBUG = False


class RootURLCache:
    def __init__(self, adb_client: AsyncDatabaseClient | None = None):
        if adb_client is None:
            adb_client = AsyncDatabaseClient()
        self.adb_client = adb_client
        self.cache = None

    async def save_to_cache(self, url: str, title: str) -> None:
        if url in self.cache:
            return
        self.cache[url] = title
        await self.adb_client.add_to_root_url_cache(url=url, page_title=title)

    async def get_from_cache(self, url: str) -> str | None:
        if self.cache is None:
            self.cache = await self.adb_client.load_root_url_cache()

        if url in self.cache:
            return self.cache[url]
        return None

    async def get_request(self, url: str) -> RootURLCacheResponseInfo:
        async with ClientSession() as session:
            try:
                async with session.get(url, headers=REQUEST_HEADERS, timeout=120) as response:
                    response.raise_for_status()
                    text = await response.text()
                    return RootURLCacheResponseInfo(text=text)
            except Exception as e:
                return RootURLCacheResponseInfo(exception=e)

    async def get_title(self, url) -> str:
        if not url.startswith('http'):
            url = "https://" + url

        parsed_url = urlparse(url)
        root_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

        title = await self.get_from_cache(root_url)
        if title is not None:
            return title

        response_info = await self.get_request(root_url)
        if response_info.exception is not None:
            return self.handle_exception(response_info.exception)

        title = await self.get_title_from_soup(response_info.text)

        await self.save_to_cache(url=root_url, title=title)

        return title

    async def get_title_from_soup(self, text: str) -> str:
        soup = BeautifulSoup(text, 'html.parser')
        try:
            title = soup.find('title').text
        except AttributeError:
            title = ""
        # Prevents most bs4 memory leaks
        if soup.html:
            soup.html.decompose()
        return title

    def handle_exception(self, e):
        if DEBUG:
            return f"Error retrieving title: {e}"
        else:
            return ""
