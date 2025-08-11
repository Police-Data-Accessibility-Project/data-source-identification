import asyncio
import math
from datetime import datetime
from typing import Optional
from urllib.parse import urljoin

import aiohttp
from bs4 import ResultSet, Tag, BeautifulSoup

from src.collectors.impl.ckan.dtos.package import Package


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
