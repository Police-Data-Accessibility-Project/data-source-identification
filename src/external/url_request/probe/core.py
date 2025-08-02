import asyncio

from aiohttp import ClientSession, ClientResponseError

from src.external.url_request.probe.format import format_client_response, format_client_response_error, format_error
from src.external.url_request.probe.model import URLProbeResponse
from tqdm.asyncio import tqdm_asyncio

class URLProbeManager:

    def __init__(
        self,
        session: ClientSession
    ):
        self.session = session

    async def probe_urls(self, urls: list[str]) -> list[URLProbeResponse]:
        return await tqdm_asyncio.gather(*[self.probe_url(url) for url in urls])

    async def probe_url(self, url: str) -> URLProbeResponse:
        result = await self.head(url)
        if result.error is None:
            return result
        return await self.get(url)


    async def head(self, url: str) -> URLProbeResponse:
        try:
            async with self.session.head(url) as response:
                return format_client_response(url, response=response)
        except ClientResponseError as e:
            return format_client_response_error(url, error=e)
        except Exception as e:
            return format_error(url, error=e)

    async def get(self, url: str) -> URLProbeResponse:
        try:
            async with self.session.get(url) as response:
                return format_client_response(url, response=response)
        except ClientResponseError as e:
            return format_client_response_error(url, error=e)
        except Exception as e:
            return format_error(url, error=e)