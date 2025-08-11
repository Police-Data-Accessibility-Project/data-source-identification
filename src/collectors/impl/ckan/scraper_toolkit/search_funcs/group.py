import sys
from typing import Optional, Any

from src.collectors.impl.ckan.scraper_toolkit._api_interface import CKANAPIInterface


async def ckan_group_package_search(
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
