import abc
import asyncio
from abc import ABC

import requests
import aiohttp

from source_collectors.muckrock.classes.fetch_requests.FetchRequestBase import FetchRequest


class MuckrockNoMoreDataError(Exception):
    pass

class MuckrockServerError(Exception):
    pass

class MuckrockFetcher(ABC):

    async def get_async_request(self, url: str) -> dict | None:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()
                return await response.json()

    async def fetch(self, request: FetchRequest) -> dict | None:
        url = self.build_url(request)
        try:
            return await self.get_async_request(url)
        except requests.exceptions.HTTPError as e:
            print(f"Failed to get records on request `{url}`: {e}")
            # If code is 404, raise NoMoreData error
            if e.response.status_code == 404:
                raise MuckrockNoMoreDataError
            if 500 <= e.response.status_code < 600:
                raise MuckrockServerError
            return None

    @abc.abstractmethod
    def build_url(self, request: FetchRequest) -> str:
        pass

