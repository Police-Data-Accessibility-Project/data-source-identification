from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.dtos.url.mapping import URLMapping
from src.db.models.impl.flag.root_url.sqlalchemy import FlagRootURL
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.queries.base.builder import QueryBuilderBase
from src.db.helpers.session import session_helper as sh


class LookupRootURLsQueryBuilder(QueryBuilderBase):
    """
    Looks up URLs to see if they exist in the database as root URLs
    """

    def __init__(self, urls: list[str]):
        super().__init__()
        self.urls = urls

    async def run(self, session: AsyncSession) -> list[URLMapping]:
        query = select(
            URL.id,
            URL.url
        ).join(FlagRootURL).where(
            URL.url.in_(self.urls),
            FlagRootURL.url_id.isnot(None)
        )
        mappings = await sh.mappings(session, query=query)
        return [
            URLMapping(
                url_id=mapping["id"],
                url=mapping["url"]
            ) for mapping in mappings
        ]