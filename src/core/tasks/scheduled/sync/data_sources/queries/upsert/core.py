from typing import final

from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import override

from src.core.tasks.scheduled.sync.data_sources.queries.upsert.helpers.filter import filter_for_urls_with_ids, \
    get_mappings_for_urls_without_data_sources
from src.core.tasks.scheduled.sync.data_sources.queries.upsert.mapper import URLSyncInfoMapper
from src.core.tasks.scheduled.sync.data_sources.queries.upsert.param_manager import \
    UpsertURLsFromDataSourcesParamManager
from src.core.tasks.scheduled.sync.data_sources.queries.upsert.requester import UpsertURLsFromDataSourcesDBRequester
from src.core.tasks.scheduled.sync.data_sources.queries.upsert.url.lookup.response import \
    LookupURLForDataSourcesSyncResponse
from src.db.dtos.url.mapping import URLMapping
from src.db.queries.base.builder import QueryBuilderBase
from src.external.pdap.dtos.sync.data_sources import DataSourcesSyncResponseInnerInfo


@final
class UpsertURLsFromDataSourcesQueryBuilder(QueryBuilderBase):

    def __init__(self, sync_infos: list[DataSourcesSyncResponseInnerInfo]):
        super().__init__()
        self.sync_infos = sync_infos
        self.urls = {sync_info.url for sync_info in self.sync_infos}
        self.param_manager = UpsertURLsFromDataSourcesParamManager(
            mapper=URLSyncInfoMapper(self.sync_infos)
        )
        self._session: AsyncSession | None = None
        self._requester: UpsertURLsFromDataSourcesDBRequester | None = None
        # Need to be able to add URL ids first before adding links or other attributes

    @property
    def requester(self) -> UpsertURLsFromDataSourcesDBRequester:
        """
        Modifies:
            self._requester
        """
        if self._requester is None:
            self._requester = UpsertURLsFromDataSourcesDBRequester(self._session)
        return self._requester

    @override
    async def run(self, session: AsyncSession) -> None:
        """
        Modifies:
            self._session
        """
        self._session = session

        lookup_results = await self._lookup_urls()
        lookups_existing_urls = filter_for_urls_with_ids(lookup_results)
        await self._update_existing_urls(lookups_existing_urls)
        await self._update_agency_link(lookups_existing_urls)
        mappings_without_data_sources = get_mappings_for_urls_without_data_sources(lookup_results)
        await self._add_new_data_sources(mappings_without_data_sources)

        extant_urls = {lookup.url_info.url for lookup in lookups_existing_urls}
        urls_to_add = list(self.urls - extant_urls)
        if len(urls_to_add) == 0:
            return
        url_mappings = await self._add_new_urls(urls_to_add)
        await self._add_new_data_sources(url_mappings)
        await self._insert_agency_link(url_mappings)

    async def _lookup_urls(self):
        lookup_results = await self.requester.lookup_urls(list(self.urls))
        return lookup_results

    async def _insert_agency_link(self, url_mappings: list[URLMapping]):
        link_url_agency_insert_params = self.param_manager.insert_agency_link(
            url_mappings
        )
        await self.requester.add_new_agency_links(link_url_agency_insert_params)

    async def _update_agency_link(self, lookups_existing_urls: list[LookupURLForDataSourcesSyncResponse]):
        link_url_agency_update_params = self.param_manager.update_agency_link(
            lookups_existing_urls
        )
        await self.requester.update_agency_links(link_url_agency_update_params)

    async def _add_new_data_sources(self, url_mappings: list[URLMapping]):
        url_ds_insert_params = self.param_manager.add_new_data_sources(url_mappings)
        await self.requester.add_new_data_sources(url_ds_insert_params)

    async def _add_new_urls(self, urls: list[str]):
        url_insert_params = self.param_manager.add_new_urls(urls)
        url_mappings = await self.requester.add_new_urls(url_insert_params)
        return url_mappings

    async def _update_existing_urls(self, lookups_existing_urls: list[LookupURLForDataSourcesSyncResponse]):
        update_params = self.param_manager.update_existing_urls(lookups_existing_urls)
        await self.requester.update_existing_urls(update_params)

