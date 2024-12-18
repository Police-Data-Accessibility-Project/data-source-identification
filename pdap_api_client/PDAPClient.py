from http import HTTPStatus
from urllib import parse
from enum import Enum
from typing import Optional, List

import requests
from pydantic import BaseModel
from requests.models import PreparedRequest

from pdap_api_client.DTOs import MatchAgencyInfo

API_URL = "https://data-sources-v2.pdap.dev/api"

class Namespaces(Enum):
    AUTH = "auth"
    MATCH = "match"

class RequestType(Enum):
    POST = "POST"
    PUT = "PUT"
    GET = "GET"
    DELETE = "DELETE"

class RequestInfo(BaseModel):
    type_: RequestType
    url: str
    json: Optional[dict] = None
    headers: Optional[dict] = None
    params: Optional[dict] = None
    timeout: Optional[int] = None

class ResponseInfo(BaseModel):
    status_code: HTTPStatus
    data: Optional[dict]

request_methods = {
    RequestType.POST: requests.post,
    RequestType.PUT: requests.put,
    RequestType.GET: requests.get,
    RequestType.DELETE: requests.delete,
}
def make_request(ri: RequestInfo) -> ResponseInfo:
    response = request_methods[ri.type_](
        ri.url,
        json=ri.json,
        headers=ri.headers,
        params=ri.params,
        timeout=ri.timeout
    )
    response.raise_for_status()
    return ResponseInfo(
        status_code=response.status_code,
        data=response.json()
    )




class URLBuilder:

    def __init__(self):
        self.base_url = API_URL

    def build_url(
        self,
        namespace: Namespaces,
        subdomains: Optional[list[str]] = None,
    ):
        url = f"{self.base_url}/{namespace.value}"
        if subdomains is not None:
            url = f"{url}/{'/'.join(subdomains)}"
        return url

def build_url(
    namespace: Namespaces,
    subdomains: Optional[list[str]] = None
):
    url = f"{API_URL}/{namespace.value}"
    if subdomains is not None:
        url = f"{url}/{'/'.join(subdomains)}"
    return url

class AccessManager:
    """
    Manages login, api key, access and refresh tokens
    """
    def __init__(self, email: str, password: str, api_key: Optional[str]):
        self.url_builder = URLBuilder()
        self.access_token = None
        self.refresh_token = None
        self.api_key = None
        self.login(email=email, password=password)

    # TODO: Add means to refresh if token expired.

    def load_api_key(self):
        url = build_url(
            namespace=Namespaces.AUTH,
            subdomains=["api-key"]
        )
        request_info = RequestInfo(
            url=url,
            headers=self.jwt_header()
        )
        response_info = make_request(request_info)
        self.api_key = response_info.data["api_key"]

    def login(self, email: str, password: str):
        url = build_url(
            namespace=Namespaces.AUTH,
            subdomains=["login"]
        )
        request_info = RequestInfo(
            url=url,
            json={
                "email": email,
                "password": password
            }
        )
        response_info = make_request(request_info)
        data = response_info.data
        self.access_token = data["access_token"]
        self.refresh_token = data["refresh_token"]


    def jwt_header(self) -> dict:
        """
        Retrieve JWT header
        Returns: Dictionary of Bearer Authorization with JWT key
        """
        return {
            "Authorization": f"Bearer {self.access_token}"
        }

    def api_key_header(self):
        """
        Retrieve API key header
        Returns: Dictionary of Basic Authorization with API key

        """
        if self.api_key is None:
            self.load_api_key()
        return {
            "Authorization": f"Basic {self.api_key}"
        }


class PDAPClient:

    def __init__(self, access_manager: AccessManager):
        self.access_manager = access_manager

    def match_agency(
            self,
            name: str,
            state: str,
            county: str,
            locality: str
    ) -> List[MatchAgencyInfo]:
        url = build_url(
            namespace=Namespaces.MATCH,
            subdomains=["agency"]
        )
        request_info = RequestInfo(
            url=url,
            json={
                "name": name,
                "state": state,
                "county": county,
                "locality": locality
            }
        )
        response_info = make_request(request_info)
        return [MatchAgencyInfo(**agency) for agency in response_info.data["agencies"]]


    def check_for_unique_source_url(self, url: str):
        pass