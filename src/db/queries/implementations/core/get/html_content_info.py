from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.dtos.url.html_content import URLHTMLContentInfo
from src.db.models.impl.url.html.content.sqlalchemy import URLHTMLContent
from src.db.queries.base.builder import QueryBuilderBase


class GetHTMLContentInfoQueryBuilder(QueryBuilderBase):

    def __init__(self, url_id: int):
        super().__init__()
        self.url_id = url_id

    async def run(self, session: AsyncSession) -> list[URLHTMLContentInfo]:
        session_result = await session.execute(
            select(URLHTMLContent)
            .where(URLHTMLContent.url_id == self.url_id)
        )
        results = session_result.scalars().all()
        return [URLHTMLContentInfo(**result.__dict__) for result in results]

