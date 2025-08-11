from typing import Optional

import requests
from aiohttp import ClientSession

from src.collectors.impl.muckrock.api_interface.lookup_response import AgencyLookupResponse
from src.collectors.impl.muckrock.enums import AgencyLookupResponseType


class MuckrockAPIInterface:

    def __init__(self, session: Optional[ClientSession] = None):
        self.base_url = "https://www.muckrock.com/api_v1/"
        self.session = session

    def build_url(self, subpath: str):
        return f"{self.base_url}{subpath}"


    async def lookup_agency(self, muckrock_agency_id: int) -> AgencyLookupResponse:
        url = self.build_url(f"agency/{muckrock_agency_id}")
        try:
            async with self.session.get(url) as results:
                results.raise_for_status()
                json = await results.json()
                name = json["name"]
                return AgencyLookupResponse(
                    name=name, type=AgencyLookupResponseType.FOUND
                )
        except requests.exceptions.HTTPError as e:
            return AgencyLookupResponse(
                name=None,
                type=AgencyLookupResponseType.ERROR,
                error=str(e)
            )
        except KeyError:
            return AgencyLookupResponse(
                name=None, type=AgencyLookupResponseType.NOT_FOUND
            )

