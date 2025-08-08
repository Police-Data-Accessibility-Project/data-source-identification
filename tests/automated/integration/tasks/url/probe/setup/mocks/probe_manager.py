from aiohttp import ClientSession

from src.external.url_request.probe.models.response import URLProbeResponse
from tests.automated.integration.tasks.url.probe.setup.format import build_url_to_probe_response_map


class MockURLProbeManager:

    def __init__(
        self,
        session: ClientSession
    ):
        self.session = session
        self._url_to_probe_response: dict[str, URLProbeResponse] = build_url_to_probe_response_map()

    async def probe_urls(self, urls: list[str]) -> list[URLProbeResponse]:
        return [
            self._url_to_probe_response[url]
            for url in urls
        ]