from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.collectors.enums import URLStatus
from src.db.models.instantiations.url.core.sqlalchemy import URL
from src.db.queries.base.builder import QueryBuilderBase


class HasValidatedURLsQueryBuilder(QueryBuilderBase):

    async def run(self, session: AsyncSession) -> bool:
        query = (
            select(URL)
            .where(URL.status == URLStatus.VALIDATED.value)
        )
        urls = await session.execute(query)
        urls = urls.scalars().all()
        return len(urls) > 0