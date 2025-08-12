from src.core.tasks.scheduled.impl.sync.data_sources.queries.upsert.agency.params import \
    UpdateLinkURLAgencyForDataSourcesSyncParams
from src.core.tasks.scheduled.impl.sync.data_sources.queries.upsert.helpers.convert import convert_to_url_update_params, \
    convert_to_url_insert_params
from src.core.tasks.scheduled.impl.sync.data_sources.queries.upsert.mapper import URLSyncInfoMapper
from src.core.tasks.scheduled.impl.sync.data_sources.queries.upsert.url.insert.params import \
    InsertURLForDataSourcesSyncParams
from src.core.tasks.scheduled.impl.sync.data_sources.queries.upsert.url.lookup.response import \
    LookupURLForDataSourcesSyncResponse
from src.core.tasks.scheduled.impl.sync.data_sources.queries.upsert.url.update.params import \
    UpdateURLForDataSourcesSyncParams
from src.db.dtos.url.mapping import URLMapping
from src.db.models.impl.link.url_agency.pydantic import LinkURLAgencyPydantic
from src.db.models.impl.url.data_source.pydantic import URLDataSourcePydantic


class UpsertURLsFromDataSourcesParamManager:
    def __init__(
        self,
        mapper: URLSyncInfoMapper
    ):
        self._mapper = mapper

    def update_existing_urls(
        self,
        lookup_results: list[LookupURLForDataSourcesSyncResponse]
    ) -> list[UpdateURLForDataSourcesSyncParams]:
        results = []
        for lookup_result in lookup_results:
            url_info = lookup_result.url_info
            sync_info = self._mapper.get(url_info.url)
            update_params = convert_to_url_update_params(
                url_id=url_info.url_id,
                sync_info=sync_info
            )
            results.append(update_params)
        return results

    def add_new_urls(
        self,
        urls: list[str]
    ) -> list[InsertURLForDataSourcesSyncParams]:
        results = []
        for url in urls:
            sync_info = self._mapper.get(url)
            insert_params = convert_to_url_insert_params(
                url=url,
                sync_info=sync_info
            )
            results.append(insert_params)
        return results

    def update_agency_link(
        self,
        lookup_results: list[LookupURLForDataSourcesSyncResponse]
    ) -> list[UpdateLinkURLAgencyForDataSourcesSyncParams]:
        results = []
        for lookup_result in lookup_results:
            url_info = lookup_result.url_info
            sync_info = self._mapper.get(url_info.url)
            update_params = UpdateLinkURLAgencyForDataSourcesSyncParams(
                url_id=url_info.url_id,
                new_agency_ids=sync_info.agency_ids,
                old_agency_ids=url_info.agency_ids
            )
            results.append(update_params)
        return results

    def insert_agency_link(
        self,
        url_mappings: list[URLMapping]
    ) -> list[LinkURLAgencyPydantic]:
        results = []
        for mapping in url_mappings:
            sync_info = self._mapper.get(mapping.url)
            for agency_id in sync_info.agency_ids:
                results.append(
                    LinkURLAgencyPydantic(
                        url_id=mapping.url_id,
                        agency_id=agency_id
                    )
                )

        return results

    def add_new_data_sources(
        self,
        mappings: list[URLMapping]
    ) -> list[URLDataSourcePydantic]:
        results = []
        for mapping in mappings:
            sync_info = self._mapper.get(mapping.url)
            results.append(
                URLDataSourcePydantic(
                    data_source_id=sync_info.id,
                    url_id=mapping.url_id
                )
            )
        return results


