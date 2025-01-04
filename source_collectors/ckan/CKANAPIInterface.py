from typing import Optional

from ckanapi import RemoteCKAN

# TODO: Maybe return Base Models?

class CKANAPIInterface:
    """
    Interfaces with the CKAN API
    """

    def __init__(self, base_url: str):
        self.remote = RemoteCKAN(base_url, get_only=True)

    def package_search(self, query: str, rows: int, start: int, **kwargs):
        return self.remote.action.package_search(q=query, rows=rows, start=start, **kwargs)
        # TODO: Add Schema

    def get_organization(self, organization_id: str):
        return self.remote.action.organization_show(id=organization_id, include_datasets=True)
        # TODO: Add Schema

    def get_group_package(self, group_package_id: str, limit: Optional[int]):
        return self.remote.action.group_package_show(id=group_package_id, limit=limit)
        # TODO: Add Schema

