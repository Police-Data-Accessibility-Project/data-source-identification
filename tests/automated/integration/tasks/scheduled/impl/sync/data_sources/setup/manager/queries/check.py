from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.db.models.instantiations.url.core.sqlalchemy import URL
from src.db.models.instantiations.url.data_source.sqlalchemy import URLDataSource
from src.db.queries.base.builder import QueryBuilderBase
from tests.automated.integration.tasks.scheduled.impl.sync.data_sources.setup.models.url.post import TestURLPostSetupRecord
from src.db.helpers.session import session_helper as sh


class CheckURLQueryBuilder(QueryBuilderBase):

    def __init__(self, record: TestURLPostSetupRecord):
        super().__init__()
        self.record = record

    async def run(self, session: AsyncSession) -> None:
        """Check if url and associated properties match record.
        Raises:
            AssertionError: if url and associated properties do not match record
        """
        query = (
            select(URL)
            .options(
                selectinload(URL.data_source),
                selectinload(URL.confirmed_agencies),
            )
            .outerjoin(URLDataSource, URL.id == URLDataSource.url_id)
        )
        if self.record.url_id is not None:
            query = query.where(URL.id == self.record.url_id)
        if self.record.data_sources_id is not None:
            query = query.where(URLDataSource.data_source_id == self.record.data_sources_id)

        result = await sh.one_or_none(session=session, query=query)
        assert result is not None, f"URL not found for {self.record}"
        await self.check_results(result)

    async def check_results(self, url: URL):
        assert url.record_type == self.record.final_record_type
        assert url.description == self.record.final_description
        assert url.name == self.record.final_name
        agencies = [agency.agency_id for agency in url.confirmed_agencies]
        assert set(agencies) == set(self.record.final_agency_ids)
        assert url.status == self.record.final_url_status
