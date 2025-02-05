from typing import Optional

from pdap_api_client.AccessManager import build_url, AccessManager
from pdap_api_client.DTOs import MatchAgencyInfo, UniqueURLDuplicateInfo, UniqueURLResponseInfo, Namespaces, \
    RequestType, RequestInfo, MatchAgencyResponse
from pdap_api_client.enums import MatchAgencyResponseStatus


class PDAPClient:

    def __init__(
            self,
            access_manager: AccessManager,
    ):
        self.access_manager = access_manager

    async def match_agency(
            self,
            name: str,
            state: Optional[str] = None,
            county: Optional[str] = None,
            locality: Optional[str] = None
    ) -> MatchAgencyResponse:
        # TODO: Change to async
        """
        Returns agencies, if any, that match or partially match the search criteria
        """
        url = build_url(
            namespace=Namespaces.MATCH,
            subdomains=["agency"]
        )
        headers = await self.access_manager.jwt_header()
        headers['Content-Type'] = "application/json"
        request_info = RequestInfo(
            type_=RequestType.POST,
            url=url,
            headers=headers,
            json={
                "name": name,
                "state": state,
                "county": county,
                "locality": locality
            }
        )
        response_info = await self.access_manager.make_request(request_info)

        matches = [
            MatchAgencyInfo(
                id = agency['id'],
                submitted_name=agency['name'],
                state=agency['state'],
                county=agency['county'],
                locality=agency['locality']
            )
            for agency in response_info.data["agencies"]]
        return MatchAgencyResponse(
            status=MatchAgencyResponseStatus(response_info.data["status"]),
            matches=matches
        )


    async def is_url_unique(
        self,
        url_to_check: str
    ) -> UniqueURLResponseInfo:
        """
        Check if a URL is unique. Returns duplicate info otherwise
        """
        url = build_url(
            namespace=Namespaces.CHECK,
            subdomains=["unique-url"]
        )
        request_info = RequestInfo(
            type_=RequestType.GET,
            url=url,
            params={
                "url": url_to_check
            }
        )
        response_info = await self.access_manager.make_request(request_info)
        duplicates = [UniqueURLDuplicateInfo(**entry) for entry in response_info.data["duplicates"]]
        is_unique = (len(duplicates) == 0)
        return UniqueURLResponseInfo(
            is_unique=is_unique,
            duplicates=duplicates
        )
