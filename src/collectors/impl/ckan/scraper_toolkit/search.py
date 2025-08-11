"""Retrieves packages from CKAN data portals and parses relevant information then outputs to a CSV file"""

import sys
from itertools import chain
from typing import Any, Callable, Optional

from from_root import from_root
from tqdm import tqdm

from src.collectors.impl.ckan.scraper_toolkit.search_funcs.collection import ckan_collection_search
from src.collectors.impl.ckan.dtos.package import Package
from src.collectors.impl.ckan.constants import CKAN_DATA_TYPES, CKAN_TYPE_CONVERSION_MAPPING

p = from_root(".pydocstyle").parent
sys.path.insert(1, str(p))


async def perform_search(
    search_func: Callable,
    search_terms: list[dict[str, Any]],
    results: list[dict[str, Any]],
):
    """Executes a search function with the given search terms.

    :param search: The search function to execute.
    :param search_terms: The list of urls and search terms.
        In the package search template, this is "url", "terms"
        In the group and organization search template, this is "url", "ids"
    :param results: The list of results.
    :return: Updated list of results.
    """
    print(f"Performing search: {search_func.__name__}")
    key = list(search_terms[0].keys())[1]
    for search in tqdm(search_terms):
        item_results = []
        for item in search[key]:
            item_result = await search_func(search["url"], item)
            item_results.append(item_result)
        results += item_results

    return results




async def get_collections(result):
    if "extras" not in result.keys():
        return []

    collections = []
    for extra in result["extras"]:
        if parent_package_has_no_resources(extra=extra, result=result):
            collections.append(await ckan_collection_search(
                base_url="https://catalog.data.gov/dataset/",
                collection_id=result["id"],
            ))
    return collections


def filter_result(result: dict[str, Any] | Package) -> bool:
    """Filters the result based on the defined criteria.

    :param result: The result to filter.
    :return: True if the result should be included, False otherwise.
    """
    if isinstance(result, Package) or "extras" not in result.keys():
        return True

    for extra in result["extras"]:
        if parent_package_has_no_resources(extra, result):
            return False
        elif package_non_public(extra):
            return False

    if no_resources_available(result):
        landing_page = get_landing_page(result)
        if landing_page is None:
            return False

    return True


def get_landing_page(result):
    landing_page = next(
        (extra for extra in result["extras"] if extra["key"] == "landingPage"), None
    )
    return landing_page


def package_non_public(extra: dict[str, Any]) -> bool:
    return extra["key"] == "accessLevel" and extra["value"] == "non-public"


def parent_package_has_no_resources(
        extra: dict[str, Any] ,
        result: dict[str, Any]
) -> bool:
    return extra["key"] == "collection_metadata" and extra["value"] == "true" and not result["resources"]


def parse_result(result: dict[str, Any] | Package) -> dict[str, Any]:
    """Retrieves the important information from the package.

    :param result: The result to parse.
    :return: The parsed result as a dictionary.
    """
    package = Package()

    if isinstance(result, Package):
        package.record_format = get_record_format_list(package)
        return package.to_dict()

    package.record_format = get_record_format_list(
        package=package, resources=result["resources"]
    )

    package = get_source_url(result, package)
    package.title = result["title"]
    package.description = result["notes"]
    package.agency_name = result["organization"]["title"]
    package.supplying_entity = get_supplying_entity(result)
    package.source_last_updated = result["metadata_modified"][0:10]

    return package.to_dict()

def get_record_format_list(
    package: Package,
    resources: Optional[list[dict[str, Any]]] = None,
) -> list[str]:
    """Retrieves the record formats from the package's resources.

    :param package: The package to retrieve record formats from.
    :param resources: The list of resources.
    :return: List of record formats.
    """
    if resources is None:
        resources = package.record_format
        package.record_format = []

    for resource in resources:
        format = get_initial_format(resource)
        format = optionally_apply_format_type_conversion(format)
        optionally_add_record_format_to_package(format, package)
        optionally_add_other_to_record_format(format, package)

    return package.record_format


def optionally_add_other_to_record_format(format, package):
    if format not in CKAN_DATA_TYPES:
        package.record_format.append("Other")


def optionally_add_record_format_to_package(format, package):
    # Add the format to the package's record format list if it's not already there and is a valid data type
    if format not in package.record_format and format in CKAN_DATA_TYPES:
        package.record_format.append(format)


def optionally_apply_format_type_conversion(format):
    # Is the format one of our conversion types?
    if format in CKAN_TYPE_CONVERSION_MAPPING.keys():
        format = CKAN_TYPE_CONVERSION_MAPPING[format]
    return format


def get_initial_format(resource):
    if isinstance(resource, str):
        format = resource
    else:
        format = resource["format"]
    return format


def get_source_url(result: dict[str, Any], package: Package) -> Package:
    """Retrieves the source URL from the package's resources.

    :param result: The result to retrieve source URL from.
    :param package: The package to update with the source URL.
    :return: The updated package.
    """
    if only_one_link_resource_available(package, result):
        set_url_from_link_to_external_page(package, result)
    elif no_resources_available(result):
        set_url_from_external_landing_page(package, result)
        package.record_format = ["HTML text"]
    else:
        set_url_from_dataset_information_page(package, result)
        package.data_portal_type = "CKAN"

    return package


def no_resources_available(result):
    return len(result["resources"]) == 0


def only_one_link_resource_available(package, result):
    return len(result["resources"]) == 1 and package.record_format == ["HTML text"]


def set_url_from_dataset_information_page(package, result):
    package.url = f"{result['base_url']}dataset/{result['name']}"


def set_url_from_link_to_external_page(package, result):
    # Use the link to the external page
    package.url = result["resources"][0]["url"]


def set_url_from_external_landing_page(package, result):
    url = [
        extra["value"]
        for extra in result["extras"]
        if extra["key"] == "landingPage"
    ]
    if len(url) > 1:
        raise ValueError("Multiple landing pages found")
    package.url = url[0]


def get_supplying_entity(result: dict[str, Any]) -> str:
    """Retrieves the supplying entity from the package's extras.

    :param result: The result to retrieve supplying entity from.
    :return: The supplying entity.
    """
    if "extras" not in result.keys():
        return result["organization"]["title"]

    for extra in result["extras"]:
        if extra["key"] == "publisher":
            return extra["value"]

    return result["organization"]["title"]


def get_flat_list(results):
    flat_list = list(chain(*results))
    return flat_list


def deduplicate_entries(flat_list):
    flat_list = [i for n, i in enumerate(flat_list) if i not in flat_list[n + 1:]]
    return flat_list


