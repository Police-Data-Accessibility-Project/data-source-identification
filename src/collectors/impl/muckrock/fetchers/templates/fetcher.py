import abc
from abc import ABC

import requests
import aiohttp

from src.collectors.impl.muckrock.fetch_requests.base import FetchRequest
from src.collectors.impl.muckrock.exceptions import MuckrockNoMoreDataError, MuckrockServerError


class MuckrockFetcherBase(ABC):

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

