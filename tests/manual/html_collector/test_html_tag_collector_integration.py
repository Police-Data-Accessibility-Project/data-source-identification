import polars as pl
import pytest

from collector_db.AsyncDatabaseClient import AsyncDatabaseClient
from collector_db.DTOs.URLInfo import URLInfo
from collector_db.DatabaseClient import DatabaseClient
from core.classes.URLHTMLCycler import URLHTMLCycler
from helpers.DBDataCreator import DBDataCreator
from html_tag_collector.ResponseParser import HTMLResponseParser
from html_tag_collector.RootURLCache import RootURLCache
from html_tag_collector.URLRequestInterface import URLRequestInterface
from html_tag_collector.collector import process_in_batches

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

def test_collector_main():
    """
    Test main function from collector module for manual inspection
    Involves live connection to and pulling of internet data
    """
    df = pl.DataFrame(sample_json_data)

    cumulative_df = process_in_batches(
        df=df,
        render_javascript=False
    )

    print(cumulative_df)
    # print data from each row, for each column
    for i in range(len(cumulative_df)):
        for col in cumulative_df.columns:
            print(f"{col}: {cumulative_df[col][i]}")

@pytest.mark.asyncio
async def test_get_response():
    uri = URLRequestInterface()
    results = await uri.make_requests(URLS)
    print(results)

@pytest.mark.asyncio
async def test_get_response_with_javascript():
    uri = URLRequestInterface()
    results = await uri.make_requests(URLS, render_javascript=True)
    print(results)

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


    cycler = URLHTMLCycler(
        adb_client=AsyncDatabaseClient(),
        url_request_interface=URLRequestInterface(),
        html_parser=HTMLResponseParser(
            root_url_cache=RootURLCache()
        )
    )
    await cycler.cycle()