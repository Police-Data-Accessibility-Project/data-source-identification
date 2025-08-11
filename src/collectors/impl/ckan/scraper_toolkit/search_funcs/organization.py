from typing import Any

from src.collectors.impl.ckan.scraper_toolkit._api_interface import CKANAPIInterface
from src.collectors.impl.ckan.scraper_toolkit.search_funcs.package import ckan_package_search


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
