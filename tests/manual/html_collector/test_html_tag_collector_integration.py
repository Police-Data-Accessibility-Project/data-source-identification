import pytest

from src.core.tasks.operators.url_html import URLHTMLTaskOperator
from tests.helpers.db_data_creator import DBDataCreator
from src.core.tasks.operators.url_html.scraper import HTMLResponseParser
from src.core.tasks.operators.url_html.scraper.request_interface import URLRequestInterface

URLS = [
    "https://pdap.io",
    "https://pdapio.io",
    "https://pdap.dev",
    "https://pdap.io/404test",
    "https://books.toscrape.com/catalogue/category/books/womens-fiction_9/index.html",

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
    results = await uri.make_requests_with_html(URLS)
    print(results)

@pytest.mark.asyncio
async def test_get_response_with_javascript():
    uri = URLRequestInterface()
    results = await uri.make_requests_with_html(URLS)
    print(results)


@pytest.mark.asyncio
async def test_get_response_with_javascript_404():
    uri = URLRequestInterface()
    results = await uri.make_requests_with_html(
        [
            'https://data.tempe.gov/apps/tempegov::1-05-feeling-of-safety-in-your-neighborhood-dashboard'
        ]
    )
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
    adb_client: AsyncDatabaseClient = db_data_creator.adb_client
    url_infos = []
    for url in URLS:
        url_infos.append(URLInfo(url=url))
    await adb_client.insert_urls(url_infos=url_infos, batch_id=batch_id)


    operator = URLHTMLTaskOperator(
        adb_client=adb_client,
        url_request_interface=URLRequestInterface(),
        html_parser=HTMLResponseParser(
            root_url_cache=RootURLCache()
        )
    )
    await operator.run_task()