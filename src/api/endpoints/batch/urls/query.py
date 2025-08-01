from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.instantiations.link.batch_url import LinkBatchURL
from src.db.models.instantiations.url.core.pydantic.info import URLInfo
from src.db.models.instantiations.url.core.sqlalchemy import URL
from src.db.queries.base.builder import QueryBuilderBase


class GetURLsByBatchQueryBuilder(QueryBuilderBase):

    def __init__(
        self,
        batch_id: int,
        page: int = 1
    ):
        super().__init__()
        self.batch_id = batch_id
        self.page = page

    async def run(self, session: AsyncSession) -> list[URLInfo]:
        query = (
            Select(URL)
            .join(LinkBatchURL)
            .where(LinkBatchURL.batch_id == self.batch_id)
            .order_by(URL.id)
            .limit(100)
            .offset((self.page - 1) * 100))
        result = await session.execute(query)
        urls = result.scalars().all()
        return [URLInfo(**url.__dict__) for url in urls]