import sys
from typing import Optional, Any

from src.collectors.impl.ckan.scraper_toolkit._api_interface import CKANAPIInterface


async def ckan_package_search(
    base_url: str,
    query: Optional[str] = None,
    rows: Optional[int] = sys.maxsize,
    start: Optional[int] = 0,
    **kwargs,
) -> list[dict[str, Any]]:
    """Performs a CKAN package (dataset) search from a CKAN data catalog URL.

    :param base_url: Base URL to search from. e.g. "https://catalog.data.gov/"
    :param query: Search string, defaults to None. None will return all packages.
    :param rows: Maximum number of results to return, defaults to maximum integer.
    :param start: Offsets the results, defaults to 0.
    :param kwargs: See https://docs.ckan.org/en/2.10/api/index.html#ckan.logic.action.get.package_search for additional arguments.
    :return: List of dictionaries representing the CKAN package search results.
    """
    interface = CKANAPIInterface(base_url)
    results = []
    offset = start
    rows_max = 1000  # CKAN's package search has a hard limit of 1000 packages returned at a time by default

    while start < rows:
        num_rows = rows - start + offset
        packages: dict = await interface.package_search(
            query=query, rows=num_rows, start=start, **kwargs
        )
        add_base_url_to_packages(base_url, packages)
        results += packages["results"]

        total_results = packages["count"]
        if rows > total_results:
            rows = total_results

        result_len = len(packages["results"])
        # Check if the website has a different rows_max value than CKAN's default
        if result_len != rows_max and start + rows_max < total_results:
            rows_max = result_len

        start += rows_max

    return results


def add_base_url_to_packages(base_url, packages):
    # Add the base_url to each package
    [package.update(base_url=base_url) for package in packages["results"]]
