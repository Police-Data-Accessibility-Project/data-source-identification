import types

from src.core.tasks.url.operators.url_html.core import URLHTMLTaskOperator
from src.core.tasks.url.operators.url_html.scraper.parser.core import HTMLResponseParser

from src.core.tasks.url.operators.url_html.scraper.request_interface.core import URLRequestInterface
from src.core.tasks.url.operators.url_html.scraper.root_url_cache.core import RootURLCache
from src.db.client.async_ import AsyncDatabaseClient
from tests.automated.integration.tasks.url.html.mocks.methods import mock_make_requests, mock_get_from_cache, mock_parse


async def setup_mocked_url_request_interface() -> URLRequestInterface:
    url_request_interface = URLRequestInterface()
    url_request_interface.make_requests_with_html = types.MethodType(mock_make_requests, url_request_interface)
    return url_request_interface


async def setup_mocked_root_url_cache() -> RootURLCache:
    mock_root_url_cache = RootURLCache()
    mock_root_url_cache.get_from_cache = types.MethodType(mock_get_from_cache, mock_root_url_cache)
    return mock_root_url_cache


async def setup_urls(db_data_creator) -> list[int]:
    batch_id = db_data_creator.batch()
    url_mappings = db_data_creator.urls(batch_id=batch_id, url_count=3).url_mappings
    url_ids = [url_info.url_id for url_info in url_mappings]
    return url_ids


async def setup_operator() -> URLHTMLTaskOperator:
    html_parser = HTMLResponseParser(
        root_url_cache=await setup_mocked_root_url_cache()
    )
    html_parser.parse = types.MethodType(mock_parse, html_parser)
    operator = URLHTMLTaskOperator(
        adb_client=AsyncDatabaseClient(),
        url_request_interface=await setup_mocked_url_request_interface(),
        html_parser=html_parser
    )
    return operator
