from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tasks.scheduled.impl.sync.data_sources.queries.upsert.url.lookup.format import format_agency_ids_result
from src.db.helpers.session import session_helper as sh
from src.core.tasks.scheduled.impl.sync.data_sources.queries.upsert.url.lookup.response import \
    LookupURLForDataSourcesSyncResponse, URLDataSyncInfo
from src.db.models.instantiations.link.url_agency.sqlalchemy import LinkURLAgency
from src.db.models.instantiations.url.core.sqlalchemy import URL
from src.db.models.instantiations.url.data_source.sqlalchemy import URLDataSource
from src.db.queries.base.builder import QueryBuilderBase


class LookupURLForDataSourcesSyncQueryBuilder(QueryBuilderBase):
    """Look up provided URLs for corresponding database entries."""

    def __init__(self, urls: list[str]):
        super().__init__()
        self.urls = urls

    async def run(self, session: AsyncSession) -> list[LookupURLForDataSourcesSyncResponse]:
        url_id_label = "url_id"
        data_source_id_label = "data_source_id"
        agency_ids_label = "agency_ids"

        query = (
            select(
                URL.url,
                URL.id.label(url_id_label),
                URLDataSource.data_source_id.label(data_source_id_label),
                func.json_agg(LinkURLAgency.agency_id).label(agency_ids_label)
            ).select_from(URL)
            .outerjoin(URLDataSource)
            .outerjoin(LinkURLAgency)
            .where(
                URL.url.in_(
                    self.urls
                )
            )
            .group_by(
                URL.url,
                URL.id,
                URLDataSource.data_source_id
            )
        )

        db_results = await sh.mappings(session=session, query=query)

        final_results = []
        for db_result in db_results:
            final_results.append(
                LookupURLForDataSourcesSyncResponse(
                    data_source_id=db_result[data_source_id_label],
                    url_info=URLDataSyncInfo(
                        url=db_result["url"],
                        url_id=db_result[url_id_label],
                        agency_ids=format_agency_ids_result(db_result[agency_ids_label])
                    )
                )
            )

        return final_results
