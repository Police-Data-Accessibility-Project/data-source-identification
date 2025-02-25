import pytest

from collector_db.AsyncDatabaseClient import AsyncDatabaseClient
from collector_db.DTOs.URLInfo import URLInfo
from core.classes.URLHTMLTaskOperator import URLHTMLTaskOperator
from helpers.DBDataCreator import DBDataCreator
from html_tag_collector.ResponseParser import HTMLResponseParser
from html_tag_collector.RootURLCache import RootURLCache
from html_tag_collector.URLRequestInterface import URLRequestInterface

URLS = [
    "https://pdap.io",
    "https://pdapio.io",
    "https://pdap.dev",
    "https://pdap.io/404test",
    "https://books.toscrape.com/catalogue/category/books/womens-fiction_9/index.html"
]

sample_json_data = [
    {
        "id": idx,
        "url": url,
        "label": "Label"
    } for idx, url in enumerate(URLS)
]

@pytest.mark.asyncio
async def test_get_response():
    uri = URLRequestInterface()
    results = await uri.make_requests(URLS)
    print(results)

@pytest.mark.asyncio
async def test_get_response_with_javascript():
    uri = URLRequestInterface()
    results = await uri.make_requests(URLS)
    print(results)

@pytest.mark.asyncio
async def test_url_html_cycle_live_data(
):
    """
    Tests the cycle on whatever exists in the DB
    """
    operator = URLHTMLTaskOperator(
        adb_client=AsyncDatabaseClient(),
        url_request_interface=URLRequestInterface(),
        html_parser=HTMLResponseParser(
            root_url_cache=RootURLCache()
        )
    )
    await operator.run_task()

@pytest.mark.asyncio
async def test_url_html_cycle(
    db_data_creator: DBDataCreator
):
    batch_id = db_data_creator.batch()
    db_client = db_data_creator.db_client
    url_infos = []
    for url in URLS:
        url_infos.append(URLInfo(url=url))
    db_client.insert_urls(url_infos=url_infos, batch_id=batch_id)


    operator = URLHTMLTaskOperator(
        adb_client=AsyncDatabaseClient(),
        url_request_interface=URLRequestInterface(),
        html_parser=HTMLResponseParser(
            root_url_cache=RootURLCache()
        )
    )
    await operator.run_task()