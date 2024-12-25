from typing import List

from pdap_api_client.AccessManager import build_url, AccessManager
from pdap_api_client.DTOs import MatchAgencyInfo, UniqueURLDuplicateInfo, UniqueURLResponseInfo, Namespaces, \
    RequestType, RequestInfo


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
        """
        Returns agencies, if any, that match or partially match the search criteria
        """
        url = build_url(
            namespace=Namespaces.MATCH,
            subdomains=["agency"]
        )
        request_info = RequestInfo(
            type_=RequestType.POST,
            url=url,
            json={
                "name": name,
                "state": state,
                "county": county,
                "locality": locality
            }
        )
        response_info = self.access_manager.make_request(request_info)
        return [MatchAgencyInfo(**agency) for agency in response_info.data["agencies"]]


    def is_url_unique(
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
        response_info = self.access_manager.make_request(request_info)
        duplicates = [UniqueURLDuplicateInfo(**entry) for entry in response_info.data["duplicates"]]
        is_unique = (len(duplicates) == 0)
        return UniqueURLResponseInfo(
            is_unique=is_unique,
            duplicates=duplicates
        )
