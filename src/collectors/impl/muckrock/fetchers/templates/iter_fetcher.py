from abc import ABC, abstractmethod

import aiohttp
import requests

from src.collectors.impl.muckrock.fetch_requests.base import FetchRequest
from src.collectors.impl.muckrock.exceptions import RequestFailureException


class MuckrockIterFetcherBase(ABC):

    def __init__(self, initial_request: FetchRequest):
        self.initial_request = initial_request

    async def get_response_async(self, url) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()
                return await response.json()

    async def get_response(self, url) -> dict:
        try:
            return await self.get_response_async(url)
        except requests.exceptions.HTTPError as e:
            print(f"Failed to get records on request `{url}`: {e}")
            raise RequestFailureException

    @abstractmethod
    def process_results(self, results: list[dict]):
        pass

    @abstractmethod
    def build_url(self, request: FetchRequest) -> str:
        pass
