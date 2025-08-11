from aiohttp import ClientSession, ClientTimeout

from src.external.url_request.dtos.url_response import URLResponseInfo
from src.external.url_request.probe.core import URLProbeManager
from src.external.url_request.probe.models.wrapper import URLProbeResponseOuterWrapper
from src.external.url_request.request import fetch_urls


class URLRequestInterface:

    @staticmethod
    async def make_requests_with_html(
        urls: list[str],
    ) -> list[URLResponseInfo]:
        return await fetch_urls(urls)

    @staticmethod
    async def probe_urls(urls: list[str]) -> list[URLProbeResponseOuterWrapper]:
        async with ClientSession(timeout=ClientTimeout(total=30)) as session:
            manager = URLProbeManager(session=session)
            return await manager.probe_urls(urls=urls)
