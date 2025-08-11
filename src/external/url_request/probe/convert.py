from http import HTTPStatus
from typing import Sequence

from aiohttp import ClientResponse, ClientResponseError

from src.external.url_request.probe.models.response import URLProbeResponse
from src.external.url_request.probe.models.redirect import URLProbeRedirectResponsePair
from src.external.url_request.probe.models.wrapper import URLProbeResponseOuterWrapper


def _process_client_response_history(history: Sequence[ClientResponse]) -> list[str]:
    return [str(cr.url) for cr in history]


def _extract_content_type(cr: ClientResponse, error: str | None) -> str | None:
    if error is None:
        return cr.content_type
    return None


def _extract_redirect_probe_response(cr: ClientResponse) -> URLProbeResponse | None:
    """Returns the probe response for the first redirect.

    This is the original URL that was probed."""
    if len(cr.history) == 0:
        return None

    all_urls = [str(cr.url) for cr in cr.history]
    first_url = all_urls[0]

    return URLProbeResponse(
        url=first_url,
        status_code=HTTPStatus.FOUND.value,
        content_type=None,
        error=None,
    )


def _extract_error(cr: ClientResponse) -> str | None:
    try:
        cr.raise_for_status()
        return None
    except ClientResponseError as e:
        return str(e)

def _has_redirect(cr: ClientResponse) -> bool:
    return len(cr.history) > 0

def _extract_source_url(cr: ClientResponse) -> str:
    return str(cr.history[0].url)

def _extract_destination_url(cr: ClientResponse) -> str:
    return str(cr.url)

def convert_client_response_to_probe_response(
    url: str,
    cr: ClientResponse
) -> URLProbeResponse | URLProbeRedirectResponsePair:
    error = _extract_error(cr)
    content_type = _extract_content_type(cr, error=error)
    if not _has_redirect(cr):
        return URLProbeResponse(
            url=str(cr.url),
            status_code=cr.status,
            content_type=content_type,
            error=error,
        )

    # Extract into separate probe responses
    source_cr = cr.history[0]  # Source CR is the first in the history
    destination_cr = cr

    destination_url = str(destination_cr.url)

    source_error = _extract_error(source_cr)
    source_content_type = _extract_content_type(source_cr, error=source_error)
    source_probe_response = URLProbeResponse(
        url=url,
        status_code=source_cr.status,
        content_type=source_content_type,
        error=source_error,
    )


    destination_error = _extract_error(destination_cr)
    destination_content_type = _extract_content_type(destination_cr, error=destination_error)
    destination_probe_response = URLProbeResponse(
        url=destination_url,
        status_code=destination_cr.status,
        content_type=destination_content_type,
        error=destination_error,
    )

    return URLProbeRedirectResponsePair(
        source=source_probe_response,
        destination=destination_probe_response
    )

def convert_to_error_response(
    url: str,
    error: str,
    status_code: int | None = None
) -> URLProbeResponseOuterWrapper:
    return URLProbeResponseOuterWrapper(
        original_url=url,
        response=URLProbeResponse(
            url=url,
            status_code=status_code,
            content_type=None,
            error=error
        )
    )
