from src.core.tasks.scheduled.impl.sync.data_sources.queries.upsert.url.lookup.response import \
    LookupURLForDataSourcesSyncResponse
from src.db.dtos.url.mapping import URLMapping


def filter_for_urls_with_ids(
    lookup_results: list[LookupURLForDataSourcesSyncResponse]
) -> list[LookupURLForDataSourcesSyncResponse]:
    return [
        lookup_result
        for lookup_result in lookup_results
        if lookup_result.url_info.url_id is not None
    ]

def get_mappings_for_urls_without_data_sources(
    lookup_results: list[LookupURLForDataSourcesSyncResponse]
) -> list[URLMapping]:
    lookups_without_data_sources = [
        lookup_result
        for lookup_result in lookup_results
        if lookup_result.data_source_id is None
    ]
    return [
        URLMapping(
            url_id=lookup_result.url_info.url_id,
            url=lookup_result.url_info.url
        )
        for lookup_result in lookups_without_data_sources
    ]