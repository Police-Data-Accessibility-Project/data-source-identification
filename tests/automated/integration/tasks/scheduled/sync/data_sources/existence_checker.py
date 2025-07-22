from collections import defaultdict

from src.db.models.instantiations.confirmed_url_agency import ConfirmedURLAgency
from src.db.models.instantiations.url.core.sqlalchemy import URL
from src.db.models.instantiations.url.data_source import URLDataSource
from src.external.pdap.dtos.sync.data_sources import DataSourcesSyncResponseInfo, DataSourcesSyncResponseInnerInfo


class URLExistenceChecker:

    def __init__(
        self,
        responses: list[DataSourcesSyncResponseInfo],
        url_ds_links: list[URLDataSource],
        url_agency_links: list[ConfirmedURLAgency]
    ):
        self._ds_id_response_dict: dict[int, DataSourcesSyncResponseInnerInfo] = {}
        for response in responses:
            for data_source in response.data_sources:
                self._ds_id_response_dict[data_source.id] = data_source
        self._ds_id_url_link_dict = {}
        for link in url_ds_links:
            self._ds_id_url_link_dict[link.data_source_id] = link.url_id
        self._url_id_agency_link_dict = defaultdict(list)
        for link in url_agency_links:
            self._url_id_agency_link_dict[link.url_id].append(link.agency_id)


    def check(self, url: URL):
        ds_id = self._ds_id_url_link_dict.get(url.id)
        if ds_id is None:
            raise AssertionError(f"URL {url.id} has no data source link")
        response = self._ds_id_response_dict.get(ds_id)
        if response is None:
            raise AssertionError(f"Data source {ds_id} has no response")

        assert response.url == url.url
        assert response.description == url.description
        assert response.name == url.name

        agency_ids = self._url_id_agency_link_dict.get(url.id)
        assert set(response.agency_ids) == set(agency_ids)