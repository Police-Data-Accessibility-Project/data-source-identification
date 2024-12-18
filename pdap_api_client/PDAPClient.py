from urllib import parse
from enum import Enum
from typing import Optional

import requests
from requests.models import PreparedRequest

API_URL = "https://data-sources-v2.pdap.dev/api"

class Namespaces(Enum):
    AUTH = "auth"


class RequestManager:
    """
    Handles making requests and managing the responses
    """




class URLBuilder:

    def __init__(self):
        self.base_url = API_URL

    def build_url(
        self,
        namespace: Namespaces,
        subdomains: Optional[list[str]] = None,
        query_parameters: Optional[dict] = None
    ):
        url = f"{self.base_url}/{namespace.value}"
        if subdomains is not None:
            url = f"{url}/{'/'.join(subdomains)}"
        if query_parameters is None:
            return url
        req = PreparedRequest()
        req.prepare_url(url, params=query_parameters)
        return req.url



class AccessManager:
    """
    Manages login, api key, access and refresh tokens
    """
    def __init__(self, email: str, password: str):
        self.url_builder = URLBuilder()

    def login(self, email: str, password: str):
        url = self.url_builder.build_url(
            namespace=Namespaces.AUTH,
            subdomains=["login"]
        )
        response = requests.post(
            url=url,
            json={
                "email": email,
                "password": password
            }
        )
        response.raise_for_status()
        # TODO: Finish


class PDAPClient:

    def __init__(self):
        pass

    def match_agency(self):
        pass

    def check_for_unique_source_url(self, url: str):
        pass