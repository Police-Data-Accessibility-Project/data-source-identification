from typing import override

from sqlalchemy.ext.asyncio import AsyncSession

from src.db.queries.base.builder import QueryBuilderBase


class CheckPrereqsForRootURLTaskQueryBuilder(QueryBuilderBase):

    @override
    async def run(self, session: AsyncSession) -> bool: