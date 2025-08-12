from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tasks.scheduled.impl.sync.data_sources.queries.upsert.agency.params import \
    UpdateLinkURLAgencyForDataSourcesSyncParams
from src.core.tasks.scheduled.impl.sync.data_sources.queries.upsert.agency.query import \
    URLAgencyLinkUpdateQueryBuilder
from src.core.tasks.scheduled.impl.sync.data_sources.queries.upsert.url.insert.params import \
    InsertURLForDataSourcesSyncParams
from src.core.tasks.scheduled.impl.sync.data_sources.queries.upsert.url.lookup.query import \
    LookupURLForDataSourcesSyncQueryBuilder
from src.core.tasks.scheduled.impl.sync.data_sources.queries.upsert.url.lookup.response import \
    LookupURLForDataSourcesSyncResponse
from src.core.tasks.scheduled.impl.sync.data_sources.queries.upsert.url.update.params import \
    UpdateURLForDataSourcesSyncParams
from src.db.dtos.url.mapping import URLMapping
from src.db.helpers.session import session_helper as sh
from src.db.models.impl.link.url_agency.pydantic import LinkURLAgencyPydantic
from src.db.models.impl.url.data_source.pydantic import URLDataSourcePydantic


class UpsertURLsFromDataSourcesDBRequester:

    def __init__(self, session: AsyncSession):
        self.session = session


    async def add_new_urls(
        self,
        params: list[InsertURLForDataSourcesSyncParams]
    ):
        url_ids = await sh.bulk_insert(
            session=self.session,
            models=params,
            return_ids=True
        )
        results = []
        for insert_param, url_id in zip(params, url_ids):
            results.append(
                URLMapping(
                    url=insert_param.url,
                    url_id=url_id,
                )
            )
        return results

    async def lookup_urls(
        self,
        urls: list[str],
    ) -> list[LookupURLForDataSourcesSyncResponse]:
        """Lookup URLs for data source sync-relevant information."""
        builder = LookupURLForDataSourcesSyncQueryBuilder(urls=urls)
        return await builder.run(session=self.session)

    async def update_existing_urls(
        self,
        params: list[UpdateURLForDataSourcesSyncParams],
    ) -> None:
        await sh.bulk_update(session=self.session, models=params)

    async def add_new_data_sources(
        self,
        params: list[URLDataSourcePydantic]
    ) -> None:
        await sh.bulk_insert(session=self.session, models=params)

    async def add_new_agency_links(
        self,
        params: list[LinkURLAgencyPydantic]
    ):
        await sh.bulk_insert(session=self.session, models=params)

    async def update_agency_links(
        self,
        params: list[UpdateLinkURLAgencyForDataSourcesSyncParams]
    ) -> None:
        """Overwrite existing url_agency links with new ones, if applicable."""
        query = URLAgencyLinkUpdateQueryBuilder(params)
        await query.run(self.session)