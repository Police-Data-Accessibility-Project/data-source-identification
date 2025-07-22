from http import HTTPStatus
from typing import Optional

from aiohttp import ClientResponseError, RequestInfo

from src.core.tasks.url.operators.url_html.scraper.parser.dtos.response_html import ResponseHTMLInfo
from src.core.tasks.url.operators.url_html.scraper.request_interface.dtos.url_response import URLResponseInfo
from tests.automated.integration.tasks.url.html.mocks.constants import MOCK_CONTENT_TYPE, MOCK_HTML_CONTENT


async def mock_make_requests(self, urls: list[str]) -> list[URLResponseInfo]:
    results = []
    for idx, url in enumerate(urls):
        # Second result should produce a 404
        if idx == 1:
            results.append(
                URLResponseInfo(
                    success=False,
                    content_type=MOCK_CONTENT_TYPE,
                    exception=str(ClientResponseError(
                        request_info=RequestInfo(
                            url=url,
                            method="GET",
                            real_url=url,
                            headers={},
                        ),
                        code=HTTPStatus.NOT_FOUND.value,
                        history=(None,),
                    )),
                    status=HTTPStatus.NOT_FOUND
                )
            )
            continue

        if idx == 2:
            # 3rd result should produce an error
            results.append(
                URLResponseInfo(
                    success=False,
                    exception=str(ValueError("test error")),
                    content_type=MOCK_CONTENT_TYPE
                ))
        else:
            # All other results should succeed
            results.append(URLResponseInfo(
                html=MOCK_HTML_CONTENT, success=True, content_type=MOCK_CONTENT_TYPE))
    return results


async def mock_parse(self, url: str, html_content: str, content_type: str) -> ResponseHTMLInfo:
    assert html_content == MOCK_HTML_CONTENT
    assert content_type == MOCK_CONTENT_TYPE
    return ResponseHTMLInfo(
        url=url,
        title="fake title",
        description="fake description",
    )


async def mock_get_from_cache(self, url: str) -> Optional[str]:
    return None
