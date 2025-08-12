from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.impl.url.core.pydantic.info import URLInfo
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.queries.base.builder import QueryBuilderBase


class GetURLInfoByURLQueryBuilder(QueryBuilderBase):

    def __init__(self, url: str):
        super().__init__()
        self.url = url

    async def run(self, session: AsyncSession) -> URLInfo | None:
        query = Select(URL).where(URL.url == self.url)
        raw_result = await session.execute(query)
        url = raw_result.scalars().first()
        return URLInfo(**url.__dict__)