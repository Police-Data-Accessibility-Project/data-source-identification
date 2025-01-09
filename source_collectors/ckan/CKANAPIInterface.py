from typing import Optional

from ckanapi import RemoteCKAN, NotFound

class CKANAPIError(Exception):
    pass

# TODO: Maybe return Base Models?

class CKANAPIInterface:
    """
    Interfaces with the CKAN API
    """

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.remote = RemoteCKAN(base_url, get_only=True)

    def package_search(self, query: str, rows: int, start: int, **kwargs):
        return self.remote.action.package_search(q=query, rows=rows, start=start, **kwargs)

    def get_organization(self, organization_id: str):
        try:
            return self.remote.action.organization_show(id=organization_id, include_datasets=True)
        except NotFound as e:
            raise CKANAPIError(f"Organization {organization_id} not found"
                               f" for url {self.base_url}. Original error: {e}")

    def get_group_package(self, group_package_id: str, limit: Optional[int]):
        try:
            return self.remote.action.group_package_show(id=group_package_id, limit=limit)
        except NotFound as e:
            raise CKANAPIError(f"Group Package {group_package_id} not found"
                               f" for url {self.base_url}. Original error: {e}")

