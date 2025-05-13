from typing import Optional

from core.DTOs.task_data_objects.SubmitApprovedURLTDO import SubmitApprovedURLTDO, SubmittedURLInfo
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


    async def is_url_duplicate(
        self,
        url_to_check: str
    ) -> bool:
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
        is_duplicate = (len(duplicates) != 0)
        return is_duplicate

    async def submit_urls(
            self,
            tdos: list[SubmitApprovedURLTDO]
    ) -> list[SubmittedURLInfo]:
        """
        Submits URLs to Data Sources App,
        modifying tdos in-place with data source id or error
        """
        request_url = build_url(
            namespace=Namespaces.SOURCE_COLLECTOR,
            subdomains=["data-sources"]
        )

        # Build url-id dictionary
        url_id_dict = {}
        for tdo in tdos:
            url_id_dict[tdo.url] = tdo.url_id

        data_sources_json = []
        for tdo in tdos:
            data_sources_json.append({
                "name": tdo.name,
                "description": tdo.description,
                "source_url": tdo.url,
                "record_type": tdo.record_type.value,
                "record_formats": tdo.record_formats,
                "data_portal_type": tdo.data_portal_type,
                "last_approval_editor": tdo.approving_user_id,
                "supplying_entity": tdo.supplying_entity,
                "agency_ids": tdo.agency_ids
            })


        headers = await self.access_manager.jwt_header()
        request_info = RequestInfo(
            type_=RequestType.POST,
            url=request_url,
            headers=headers,
            json={
                "data_sources": data_sources_json
            }
        )
        response_info = await self.access_manager.make_request(request_info)
        data_sources_response_json = response_info.data["data_sources"]

        results = []
        for data_source in data_sources_response_json:
            url = data_source["url"]
            response_object = SubmittedURLInfo(
                url_id=url_id_dict[url],
                data_source_id=data_source["data_source_id"],
                request_error=data_source["error"]
            )
            results.append(response_object)

        return results
