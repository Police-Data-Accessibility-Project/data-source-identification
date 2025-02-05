from http import HTTPStatus
from typing import Optional

import requests
from aiohttp import ClientSession

from pdap_api_client.DTOs import RequestType, Namespaces, RequestInfo, ResponseInfo

API_URL = "https://data-sources-v2.pdap.dev/api"
request_methods = {
    RequestType.POST: ClientSession.post,
    RequestType.PUT: ClientSession.put,
    RequestType.GET: ClientSession.get,
    RequestType.DELETE: ClientSession.delete,
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
    def __init__(
            self,
            session: ClientSession,
            email: str,
            password: str,
            api_key: Optional[str] = None,
    ):
        self.session = session
        self._access_token = None
        self._refresh_token = None
        self.api_key = api_key
        self.email = email
        self.password = password
        self.login(email=email, password=password)

    @property
    async def access_token(self):
        if self._access_token is None:
            await self.login(
                email=self.email,
                password=self.password
            )
        return self._access_token

    @property
    async def refresh_token(self):
        if self._refresh_token is None:
            await self.login(
                email=self.email,
                password=self.password
            )
        return self._refresh_token

    # TODO: Add means to refresh if token expired.

    async def load_api_key(self):
        url = build_url(
            namespace=Namespaces.AUTH,
            subdomains=["api-key"]
        )
        request_info = RequestInfo(
            type_ = RequestType.POST,
            url=url,
            headers=await self.jwt_header()
        )
        response_info = await self.make_request(request_info)
        self.api_key = response_info.data["api_key"]

    async def refresh_access_token(self):
        url = build_url(
            namespace=Namespaces.AUTH,
            subdomains=["refresh-session"],
        )
        refresh_token = await self.refresh_token
        rqi = RequestInfo(
            type_=RequestType.POST,
            url=url,
            json={"refresh_token": refresh_token},
            headers=await self.jwt_header()
        )
        rsi = await self.make_request(rqi)
        data = rsi.data
        self._access_token = data['access_token']
        self._refresh_token = data['refresh_token']

    async def make_request(self, ri: RequestInfo) -> ResponseInfo:
        try:
            method = getattr(self.session, ri.type_.value.lower())
            async with method(**ri.kwargs()) as response:
                response.raise_for_status()
                json = await response.json()
                return ResponseInfo(
                    status_code=HTTPStatus(response.status),
                    data=json
                )
        except requests.RequestException as e:
            # TODO: Precise string matching here is brittle. Consider changing later.
            if json.message == "Token is expired. Please request a new token.":
                await self.refresh_access_token()
                return await self.make_request(ri)
            else:
                raise CustomHTTPException(f"Error making {ri.type_} request to {ri.url}: {e}")


    async def login(self, email: str, password: str):
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
        response_info = await self.make_request(request_info)
        data = response_info.data
        self._access_token = data["access_token"]
        self._refresh_token = data["refresh_token"]


    async def jwt_header(self) -> dict:
        """
        Retrieve JWT header
        Returns: Dictionary of Bearer Authorization with JWT key
        """
        access_token = await self.access_token
        return {
            "Authorization": f"Bearer {access_token}"
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
