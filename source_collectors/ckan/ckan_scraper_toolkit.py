"""Toolkit of functions that use ckanapi to retrieve packages from CKAN data portals"""
import asyncio
import math
import sys
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional
from urllib.parse import urljoin

import aiohttp
from bs4 import BeautifulSoup, ResultSet, Tag

from source_collectors.ckan.CKANAPIInterface import CKANAPIInterface


@dataclass
class Package:
    """
    A class representing a CKAN package (dataset).
    """
    base_url: str = ""
    url: str = ""
    title: str = ""
    agency_name: str = ""
    description: str = ""
    supplying_entity: str = ""
    record_format: list = field(default_factory=lambda: [])
    data_portal_type: str = ""
    source_last_updated: str = ""

    def to_dict(self):
        """
        Returns a dictionary representation of the package.
        """
        return {
            "source_url": self.url,
            "submitted_name": self.title,
            "agency_name": self.agency_name,
            "description": self.description,
            "supplying_entity": self.supplying_entity,
            "record_format": self.record_format,
            "data_portal_type": self.data_portal_type,
            "source_last_updated": self.source_last_updated,
        }


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


async def ckan_package_search_from_organization(
    base_url: str, organization_id: str
) -> list[dict[str, Any]]:
    """Returns a list of CKAN packages from an organization. Only 10 packages are able to be returned.

    :param base_url: Base URL of the CKAN portal. e.g. "https://catalog.data.gov/"
    :param organization_id: The organization's ID.
    :return: List of dictionaries representing the packages associated with the organization.
    """
    interface = CKANAPIInterface(base_url)
    organization = await interface.get_organization(organization_id)
    packages = organization["packages"]
    results = await search_for_results(base_url, packages)

    return results


async def search_for_results(base_url, packages):
    results = []
    for package in packages:
        query = f"id:{package['id']}"
        results += await ckan_package_search(base_url=base_url, query=query)
    return results


async def ckan_group_package_show(
    base_url: str, id: str, limit: Optional[int] = sys.maxsize
) -> list[dict[str, Any]]:
    """Returns a list of CKAN packages from a group.

    :param base_url: Base URL of the CKAN portal. e.g. "https://catalog.data.gov/"
    :param id: The group's ID.
    :param limit: Maximum number of results to return, defaults to maximum integer.
    :return: List of dictionaries representing the packages associated with the group.
    """
    interface = CKANAPIInterface(base_url)
    results = await interface.get_group_package(group_package_id=id, limit=limit)
    # Add the base_url to each package
    [package.update(base_url=base_url) for package in results]
    return results


async def ckan_collection_search(base_url: str, collection_id: str) -> list[Package]:
    """Returns a list of CKAN packages from a collection.

    :param base_url: Base URL of the CKAN portal before the collection ID. e.g. "https://catalog.data.gov/dataset/"
    :param collection_id: The ID of the parent package.
    :return: List of Package objects representing the packages associated with the collection.
    """
    url = f"{base_url}?collection_package_id={collection_id}"
    soup = await _get_soup(url)

    # Calculate the total number of pages of packages
    num_results = int(soup.find(class_="new-results").text.split()[0].replace(",", ""))
    pages = math.ceil(num_results / 20)

    packages = await get_packages(base_url, collection_id, pages)

    return packages


async def get_packages(base_url, collection_id, pages):
    packages = []
    for page in range(1, pages + 1):
        url = f"{base_url}?collection_package_id={collection_id}&page={page}"
        soup = await _get_soup(url)

        packages = []
        for dataset_content in soup.find_all(class_="dataset-content"):
            await asyncio.sleep(1)
            package = await _collection_search_get_package_data(dataset_content, base_url)
            packages.append(package)

    return packages

async def _collection_search_get_package_data(dataset_content, base_url: str):
    """Parses the dataset content and returns a Package object."""
    package = Package()
    joined_url = urljoin(base_url, dataset_content.a.get("href"))
    dataset_soup = await _get_soup(joined_url)
    # Determine if the dataset url should be the linked page to an external site or the current site
    resources = get_resources(dataset_soup)
    button = get_button(resources)
    set_url_and_data_portal_type(button, joined_url, package, resources)
    package.base_url = base_url
    set_title(dataset_soup, package)
    set_agency_name(dataset_soup, package)
    set_supplying_entity(dataset_soup, package)
    set_description(dataset_soup, package)
    set_record_format(dataset_content, package)
    date = get_data(dataset_soup)
    set_source_last_updated(date, package)

    return package


def set_source_last_updated(date, package):
    package.source_last_updated = datetime.strptime(date, "%B %d, %Y").strftime(
        "%Y-%d-%m"
    )


def get_data(dataset_soup):
    return dataset_soup.find(property="dct:modified").text.strip()


def get_button(resources: ResultSet) -> Optional[Tag]:
    if len(resources) == 0:
        return None
    return resources[0].find(class_="btn-group")


def get_resources(dataset_soup):
    return dataset_soup.find("section", id="dataset-resources").find_all(
        class_="resource-item"
    )


def set_url_and_data_portal_type(
        button: Optional[Tag],
        joined_url: str,
        package: Package,
        resources: ResultSet
):
    if len(resources) == 1 and button is not None and button.a.text == "Visit page":
        package.url = button.a.get("href")
    else:
        package.url = joined_url
        package.data_portal_type = "CKAN"


def set_record_format(dataset_content, package):
    package.record_format = [
        format1.text.strip() for format1 in dataset_content.find_all("li")
    ]
    package.record_format = list(set(package.record_format))


def set_title(dataset_soup, package):
    package.title = dataset_soup.find(itemprop="name").text.strip()


def set_agency_name(dataset_soup, package):
    package.agency_name = dataset_soup.find("h1", class_="heading").text.strip()


def set_supplying_entity(dataset_soup, package):
    package.supplying_entity = dataset_soup.find(property="dct:publisher").text.strip()


def set_description(dataset_soup, package):
    package.description = dataset_soup.find(class_="notes").p.text


async def _get_soup(url: str) -> BeautifulSoup:
    """Returns a BeautifulSoup object for the given URL."""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            response.raise_for_status()
            return BeautifulSoup(await response.text(), "lxml")
