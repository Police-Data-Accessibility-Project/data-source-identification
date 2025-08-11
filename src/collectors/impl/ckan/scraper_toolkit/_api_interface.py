from typing import Optional

import aiohttp
from aiohttp import ContentTypeError

from src.collectors.impl.ckan.exceptions import CKANAPIError


class CKANAPIInterface:
    """
    Interfaces with the CKAN API
    """

    def __init__(self, base_url: str):
        self.base_url = base_url

    @staticmethod
    def _serialize_params(params: dict) -> dict:
        return {
            k: str(v).lower() if isinstance(v, bool) else str(v) for k, v in params.items()
        }

    async def _get(self, action: str, params: dict):
        url = f"{self.base_url}/api/3/action/{action}"
        serialized_params = self._serialize_params(params)
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=serialized_params) as response:
                try:
                    data = await response.json()
                    if not data.get("success", False):
                        raise CKANAPIError(f"Request failed: {data}")
                except ContentTypeError:
                    raise CKANAPIError(f"Request failed: {response.text()}")
                return data["result"]

    async def package_search(
        self,
        query: str,
        rows: int,
        start: int,
        **kwargs
    ):
        return await self._get("package_search", {
            "q": query, "rows": rows, "start": start, **kwargs
        })

    async def get_organization(
        self,
        organization_id: str
    ):
        try:
            return await self._get("organization_show", {
                "id": organization_id, "include_datasets": True
            })
        except CKANAPIError as e:
            raise CKANAPIError(
                f"Organization {organization_id} not found for url {self.base_url}. {e}"
            )

    async def get_group_package(
        self,
        group_package_id: str,
        limit: Optional[int]
    ):
        try:
            return await self._get("group_package_show", {
                "id": group_package_id, "limit": limit
            })
        except CKANAPIError as e:
            raise CKANAPIError(
                f"Group Package {group_package_id} not found for url {self.base_url}. {e}"
            )