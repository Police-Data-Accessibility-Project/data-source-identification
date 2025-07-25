from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.collectors.enums import URLStatus, CollectorType
from src.core.tasks.url.operators.agency_identification.dtos.tdo import AgencyIdentificationTDO
from src.db.models.instantiations.batch import Batch
from src.db.models.instantiations.link.link_batch_urls import LinkBatchURL
from src.db.models.instantiations.url.core import URL
from src.db.queries.base.builder import QueryBuilderBase
from src.db.statement_composer import StatementComposer


class GetPendingURLsWithoutAgencySuggestionsQueryBuilder(QueryBuilderBase):

    async def run(self, session: AsyncSession) -> list[AgencyIdentificationTDO]:

        statement = (
            select(URL.id, URL.collector_metadata, Batch.strategy)
            .select_from(URL)
            .where(URL.outcome == URLStatus.PENDING.value)
            .join(LinkBatchURL)
            .join(Batch)
        )
        statement = StatementComposer.exclude_urls_with_agency_suggestions(statement)
        statement = statement.limit(100)
        raw_results = await session.execute(statement)
        return [
            AgencyIdentificationTDO(
                url_id=raw_result[0],
                collector_metadata=raw_result[1],
                collector_type=CollectorType(raw_result[2])
            )
            for raw_result in raw_results
        ]