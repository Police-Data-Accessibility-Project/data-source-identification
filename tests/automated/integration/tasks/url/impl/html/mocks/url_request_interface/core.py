from src.external.url_request.dtos.url_response import URLResponseInfo
from tests.automated.integration.tasks.url.impl.html.mocks.url_request_interface.setup import setup_url_to_response_info


class MockURLRequestInterface:

    def __init__(self):
        self._url_to_response_info: dict[str, URLResponseInfo] = setup_url_to_response_info()

    async def make_requests_with_html(self, urls: list[str]) -> list[URLResponseInfo]:
        return [self._url_to_response_info[url] for url in urls]