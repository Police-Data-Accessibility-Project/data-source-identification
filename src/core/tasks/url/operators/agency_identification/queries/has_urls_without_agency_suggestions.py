from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.collectors.enums import URLStatus
from src.db.models.instantiations.url.core.sqlalchemy import URL
from src.db.queries.base.builder import QueryBuilderBase
from src.db.statement_composer import StatementComposer


class HasURLsWithoutAgencySuggestionsQueryBuilder(QueryBuilderBase):

    async def run(
        self,
        session: AsyncSession
    ) -> bool:
        statement = (
            select(
                URL.id
            ).where(
                URL.outcome == URLStatus.PENDING.value
            )
        )

        statement = StatementComposer.exclude_urls_with_agency_suggestions(statement)
        raw_result = await session.execute(statement)
        result = raw_result.all()
        return len(result) != 0