from enum import Enum
from typing import Optional

import requests
from aiohttp import ClientSession
from pydantic import BaseModel


class AgencyLookupResponseType(Enum):
    FOUND = "found"
    NOT_FOUND = "not_found"
    ERROR = "error"

class AgencyLookupResponse(BaseModel):
    name: Optional[str]
    type: AgencyLookupResponseType
    error: Optional[str] = None



class MuckrockAPIInterface:

    def __init__(self, session: ClientSession):
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

