from http import HTTPStatus
from typing import Optional

import requests

from pdap_api_client.DTOs import RequestType, Namespaces, RequestInfo, ResponseInfo

API_URL = "https://data-sources-v2.pdap.dev/api"
request_methods = {
    RequestType.POST: requests.post,
    RequestType.PUT: requests.put,
    RequestType.GET: requests.get,
    RequestType.DELETE: requests.delete,
}


class CustomHTTPException(Exception):
    pass


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
    def __init__(self, email: str, password: str, api_key: Optional[str] = None):
        self.access_token = None
        self.refresh_token = None
        self.api_key = api_key
        self.login(email=email, password=password)

    # TODO: Add means to refresh if token expired.

    def load_api_key(self):
        url = build_url(
            namespace=Namespaces.AUTH,
            subdomains=["api-key"]
        )
        request_info = RequestInfo(
            type_ = RequestType.POST,
            url=url,
            headers=self.jwt_header()
        )
        response_info = self.make_request(request_info)
        self.api_key = response_info.data["api_key"]

    def refresh_access_token(self):
        url = build_url(
            namespace=Namespaces.AUTH,
            subdomains=["refresh-session"],
        )
        raise NotImplementedError("Waiting on https://github.com/Police-Data-Accessibility-Project/data-sources-app/issues/566")

    def make_request(self, ri: RequestInfo) -> ResponseInfo:
        try:
            response = request_methods[ri.type_](
                ri.url,
                json=ri.json,
                headers=ri.headers,
                params=ri.params,
                timeout=ri.timeout
            )
            response.raise_for_status()
        except requests.RequestException as e:
            # TODO: Precise string matching here is brittle. Consider changing later.
            if e.response.json().message == "Token is expired. Please request a new token.":
                self.refresh_access_token()
                return self.make_request(ri)
            else:
                raise CustomHTTPException(f"Error making {ri.type_} request to {ri.url}: {e}")
        return ResponseInfo(
            status_code=HTTPStatus(response.status_code),
            data=response.json()
        )

    def login(self, email: str, password: str):
        url = build_url(
            namespace=Namespaces.AUTH,
            subdomains=["login"]
        )
        request_info = RequestInfo(
            type_=RequestType.POST,
            url=url,
            json={
                "email": email,
                "password": password
            }
        )
        response_info = self.make_request(request_info)
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
