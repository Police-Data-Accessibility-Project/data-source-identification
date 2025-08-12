from typing import Optional

from pdap_access_manager import AccessManager, DataSourcesNamespaces, RequestInfo, RequestType

from src.core.tasks.scheduled.impl.sync.agency.dtos.parameters import AgencySyncParameters
from src.core.tasks.scheduled.impl.sync.data_sources.params import DataSourcesSyncParameters
from src.core.tasks.url.operators.submit_approved.tdo import SubmitApprovedURLTDO, SubmittedURLInfo
from src.external.pdap.dtos.sync.agencies import AgenciesSyncResponseInnerInfo, AgenciesSyncResponseInfo
from src.external.pdap.dtos.match_agency.post import MatchAgencyInfo
from src.external.pdap.dtos.match_agency.response import MatchAgencyResponse
from src.external.pdap.dtos.sync.data_sources import DataSourcesSyncResponseInfo, DataSourcesSyncResponseInnerInfo
from src.external.pdap.dtos.unique_url_duplicate import UniqueURLDuplicateInfo
from src.external.pdap.enums import MatchAgencyResponseStatus


class PDAPClient:

    def __init__(
        self,
        access_manager: AccessManager,
    ):
        self.access_manager = access_manager

    async def match_agency(
        self,
        name: str,
        state: str | None = None,
        county: str | None = None,
        locality: str | None = None
    ) -> MatchAgencyResponse:
        """
        Returns agencies, if any, that match or partially match the search criteria
        """
        url = self.access_manager.build_url(
            namespace=DataSourcesNamespaces.MATCH,
            subdomains=["agency"]
        )

        headers = await self.access_manager.jwt_header()
        headers['Content-Type'] = "application/json"
        request_info = RequestInfo(
            type_=RequestType.POST,
            url=url,
            headers=headers,
            json_={
                "name": name,
                "state": state,
                "county": county,
                "locality": locality
            }
        )
        response_info = await self.access_manager.make_request(request_info)
        matches = []
        for agency in response_info.data["agencies"]:
            mai = MatchAgencyInfo(
                id=agency['id'],
                submitted_name=agency['name']
            )
            if len(agency['locations']) > 0:
                first_location = agency['locations'][0]
                mai.state = first_location['state']
                mai.county = first_location['county']
                mai.locality = first_location['locality']
            matches.append(mai)

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
        url = self.access_manager.build_url(
            namespace=DataSourcesNamespaces.CHECK,
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
        request_url = self.access_manager.build_url(
            namespace=DataSourcesNamespaces.SOURCE_COLLECTOR,
            subdomains=["data-sources"]
        )

        # Build url-id dictionary
        url_id_dict = {}
        for tdo in tdos:
            url_id_dict[tdo.url] = tdo.url_id

        data_sources_json = []
        for tdo in tdos:
            data_sources_json.append(
                {
                    "name": tdo.name,
                    "description": tdo.description,
                    "source_url": tdo.url,
                    "record_type": tdo.record_type.value,
                    "record_formats": tdo.record_formats,
                    "data_portal_type": tdo.data_portal_type,
                    "last_approval_editor": tdo.approving_user_id,
                    "supplying_entity": tdo.supplying_entity,
                    "agency_ids": tdo.agency_ids
                }
            )

        headers = await self.access_manager.jwt_header()
        request_info = RequestInfo(
            type_=RequestType.POST,
            url=request_url,
            headers=headers,
            json_={
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

    async def sync_agencies(
        self,
        params: AgencySyncParameters
    ) -> AgenciesSyncResponseInfo:
        url =self.access_manager.build_url(
            namespace=DataSourcesNamespaces.SOURCE_COLLECTOR,
            subdomains=[
                "agencies",
                "sync"
            ]
        )
        headers = await self.access_manager.jwt_header()
        headers['Content-Type'] = "application/json"
        request_info = RequestInfo(
            type_=RequestType.GET,
            url=url,
            headers=headers,
            params={
                "page": params.page,
                "updated_at": params.cutoff_date
            }
        )
        response_info = await self.access_manager.make_request(request_info)
        return AgenciesSyncResponseInfo(
            agencies=[
                AgenciesSyncResponseInnerInfo(**entry)
                for entry in response_info.data["agencies"]
            ]
        )

    async def sync_data_sources(
        self,
        params: DataSourcesSyncParameters
    ) -> DataSourcesSyncResponseInfo:
        url = self.access_manager.build_url(
            namespace=DataSourcesNamespaces.SOURCE_COLLECTOR,
            subdomains=[
                "data-sources",
                "sync"
            ]
        )
        headers = await self.access_manager.jwt_header()
        headers['Content-Type'] = "application/json"
        params_dict = {"page": params.page}
        if params.cutoff_date is not None:
            params_dict["updated_at"] = params.cutoff_date

        request_info = RequestInfo(
            type_=RequestType.GET,
            url=url,
            headers=headers,
            params=params_dict
        )
        response_info = await self.access_manager.make_request(request_info)
        return DataSourcesSyncResponseInfo(
            data_sources=[
                DataSourcesSyncResponseInnerInfo(**entry)
                for entry in response_info.data["data_sources"]
            ]
        )