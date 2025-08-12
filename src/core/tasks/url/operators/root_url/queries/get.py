from typing import override

from sqlalchemy.ext.asyncio import AsyncSession

from src.db.queries.base.builder import QueryBuilderBase


class GetURLsForRootURLTaskQueryBuilder(QueryBuilderBase):

    @override
    async def run(self, session: AsyncSession) -> None:
        raise NotImplementedError