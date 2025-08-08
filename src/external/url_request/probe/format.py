from aiohttp import ClientResponse, ClientResponseError

from src.external.url_request.probe.models.response import URLProbeResponse


def format_content_type(content_type: str) -> str:
    return content_type.split(";")[0].strip()

def format_client_response(url: str, response: ClientResponse) -> URLProbeResponse:
    return URLProbeResponse(
        url=url,
        status_code=response.status,
        content_type=format_content_type(
            response.headers.get("content-type")
        )
    )

def format_client_response_error(url: str, error: ClientResponseError) -> URLProbeResponse:
    return URLProbeResponse(
        url=url,
        status_code=error.status,
        content_type=None,
        error=str(error)
    )

def format_error(url: str, error: Exception) -> URLProbeResponse:
    return URLProbeResponse(
        url=url,
        status_code=None,
        content_type=None,
        error=str(error)
    )