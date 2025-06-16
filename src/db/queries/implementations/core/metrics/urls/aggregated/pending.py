from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from src.db.queries.base.builder import QueryBuilderBase


class GetMetricsURLSAggregatedPendingQueryBuilder(QueryBuilderBase):

    async def get_flags(self, session: AsyncSession) -> Any:
        raise NotImplementedError

    async def run(self, session: AsyncSession) -> Any:
        raise NotImplementedError

