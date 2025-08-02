from sqlalchemy.ext.asyncio import AsyncSession

from src.db.queries.base.builder import QueryBuilderBase
from src.db.statement_composer import StatementComposer


class HasPendingURsMissingMiscellaneousDataQueryBuilder(QueryBuilderBase):

    async def run(self, session: AsyncSession) -> bool:
        query = StatementComposer.pending_urls_missing_miscellaneous_metadata_query()
        query = query.limit(1)

        scalar_result = await session.scalars(query)
        return bool(scalar_result.first())