from http import HTTPStatus

from src.external.url_request.dtos.url_response import URLResponseInfo
from tests.automated.integration.tasks.url.impl.html.setup.data import TEST_ENTRIES
from tests.automated.integration.tasks.url.impl.html.setup.models.entry import TestURLHTMLTaskSetupEntry, TestErrorType
from tests.helpers.simple_test_data_functions import generate_test_html


def _get_success(
    entry: TestURLHTMLTaskSetupEntry
) -> bool:
    if entry.give_error is not None:
        return False
    return True

def get_http_status(
    entry: TestURLHTMLTaskSetupEntry
) -> HTTPStatus:
    if entry.give_error is None:
        return HTTPStatus.OK
    if entry.give_error == TestErrorType.HTTP_404:
        return HTTPStatus.NOT_FOUND
    return HTTPStatus.INTERNAL_SERVER_ERROR

def _get_content_type(
    entry: TestURLHTMLTaskSetupEntry
) -> str | None:
    if entry.give_error is not None:
        return None
    return "text/html"


def setup_url_to_response_info(
) -> dict[str, URLResponseInfo]:
    d = {}
    for entry in TEST_ENTRIES:
        response_info = URLResponseInfo(
            success=_get_success(entry),
            status=get_http_status(entry),
            html=generate_test_html() if _get_success(entry) else None,
            content_type=_get_content_type(entry),
            exception=None if _get_success(entry) else "Error"
        )
        d[entry.url_info.url] = response_info
    return d
