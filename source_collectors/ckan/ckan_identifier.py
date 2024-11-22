"""This program identifies if a given URL is a CKAN-hosted website"""

import re
import sys

import asyncio
from bs4 import BeautifulSoup
from from_root import from_root
import polars as pl
from polars.dataframe.frame import DataFrame
import requests
from requests import Response

p = from_root(".gitignore").parent
sys.path.insert(1, str(p))

from html_tag_collector.collector import run_get_response


def get_responses(urls: list[str]) -> list[Response]:
    """Uses the tag collector's run_get_response method to get response objects for each URL.

    :param urls: The list of URLs.
    :return: The list of resulting responses.
    """
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(run_get_response(urls))
    loop.run_until_complete(future)
    return future.result()


def is_ckan_hosted(response: Response) -> bool:
    """Checks if the response content contains the CKAN version tag.

    :param response: The response object.
    :return: True if the CKAN version tag is found, False otherwise.
    """
    soup = BeautifulSoup(response.content, "lxml")

    # Checks if the CKAN version tag is present, looks like this:
    # <meta name="generator" content="ckan 2.10.5">
    ckan_tag = soup.head.find(content=re.compile("ckan \d+\.\d+\.\d+"))
    if ckan_tag is not None:
        return True

    return False


def ckan_identifier(
    urls: list[str] = None, write_output_csv: bool = False
) -> DataFrame:
    """Identifies if each URL in a list is hosted using ckan.

    :param urls: List of URLs to identify, defaults to None.
    None will use a CSV file specified on the command line at runtime.
    :param write_output_csv: Whether to output the results to a CSV file, defaults to False.
    :return: Returns a DataFrame with URLs and their labels.
    """
    if urls is None:
        file = sys.argv[1]
        df = pl.read_csv(file)
    else:
        df = pl.DataFrame([pl.Series("url", urls)])

    results = get_responses(urls=list(df["url"]))

    results_df = pl.from_dicts(results)
    urls_and_responses = pl.DataFrame(
        [
            pl.Series("url", df["url"]),
            pl.Series("response", results_df["response"]),
        ]
    )

    # Add a new column indicating if the URL contains the CKAN version tag
    urls_and_responses = urls_and_responses.with_columns(
        pl.col("response")
        .map_elements(is_ckan_hosted, return_dtype=bool)
        .alias("is_ckan_hosted")
    )

    output_columns = urls_and_responses.select(["url", "is_ckan_hosted"])
    if write_output_csv is True:
        output_columns.write_csv("output.csv")

    return output_columns


if __name__ == "__main__":
    ckan_identifier(write_output_csv=True)
