from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.db.models.instantiations.agency.sqlalchemy import Agency
from src.db.models.instantiations.confirmed_url_agency import LinkURLAgency
from src.db.models.instantiations.url.core.sqlalchemy import URL
from src.db.models.instantiations.url.data_source import URLDataSource
from src.db.queries.base.builder import QueryBuilderBase
from tests.automated.integration.tasks.scheduled.sync.data_sources.setup.models.url.post import TestURLPostSetupRecord


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
            .join(URLDataSource, URL.id == URLDataSource.data_source_id)
            .outerjoin(LinkURLAgency, URL.id == LinkURLAgency.url_id)
            .join(Agency, LinkURLAgency.agency_id == Agency.agency_id)
        )
        if self.record.url_id is not None:
            query = query.where(URL.id == self.record.url_id)
        if self.record.data_sources_id is not None:
            query = query.where(URLDataSource.id == self.record.data_sources_id)

        raw_result = await session.execute(query)
        result = raw_result.scalars().one_or_none()
        assert result is not None
        await self.check_results(result)

    async def check_results(self, url: URL):
        assert url.record_type == self.record.final_record_type
        assert url.description == self.record.final_description
        assert url.name == self.record.final_name
        agencies = [agency.agency_id for agency in url.confirmed_agencies]
        assert set(agencies) == set(self.record.final_agency_ids)
        assert url.outcome == self.record.final_url_status
