from http import HTTPStatus

from aiohttp import ClientSession, InvalidUrlClientError, ClientConnectorSSLError, ClientConnectorDNSError, \
    ClientConnectorCertificateError, ClientResponseError, ClientConnectorError
from tqdm.asyncio import tqdm_asyncio

from src.external.url_request.probe.convert import convert_client_response_to_probe_response, convert_to_error_response
from src.external.url_request.probe.models.response import URLProbeResponse
from src.external.url_request.probe.models.wrapper import URLProbeResponseOuterWrapper


class URLProbeManager:

    def __init__(
        self,
        session: ClientSession
    ):
        self.session = session

    async def probe_urls(self, urls: list[str]) -> list[URLProbeResponseOuterWrapper]:
        return await tqdm_asyncio.gather(*[self._probe(url) for url in urls])

    async def _probe(self, url: str) -> URLProbeResponseOuterWrapper:
        try:
            response = await self._head(url)
            if not response.is_redirect and response.response.status_code == HTTPStatus.OK:
                return response
            # Fallback to GET if HEAD fails
            return await self._get(url)
        except InvalidUrlClientError:
            return convert_to_error_response(url, error="Invalid URL")
        except (
                ClientConnectorError,
                ClientConnectorSSLError,
                ClientConnectorDNSError,
                ClientConnectorCertificateError
        ) as e:
            return convert_to_error_response(url, error=str(e))




    async def _head(self, url: str) -> URLProbeResponseOuterWrapper:
        try:
            async with self.session.head(url, allow_redirects=True) as response:
                return URLProbeResponseOuterWrapper(
                    original_url=url,
                    response=convert_client_response_to_probe_response(response)
                )
        except ClientResponseError as e:
            return convert_to_error_response(
                url,
                error=str(e),
                status_code=e.status
            )

    async def _get(self, url: str) -> URLProbeResponseOuterWrapper:
        try:
            async with self.session.get(url, allow_redirects=True) as response:
                return URLProbeResponseOuterWrapper(
                    original_url=url,
                    response=convert_client_response_to_probe_response(response)
                )
        except ClientResponseError as e:
            return convert_to_error_response(
                url,
                error=str(e),
                status_code=e.status
            )
