from aiohttp import ClientResponse, ClientResponseError

from src.external.url_request.probe.models.response import URLProbeResponse


def format_content_type(content_type: str) -> str:
    return content_type.split(";")[0].strip()
