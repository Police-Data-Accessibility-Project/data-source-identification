from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.dtos.url.mapping import URLMapping
from src.db.helpers.session import session_helper as sh
from src.db.models.impl.flag.root_url.sqlalchemy import FlagRootURL
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.queries.base.builder import QueryBuilderBase


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
        )
        mappings = await sh.mappings(session, query=query)

        root_urls_to_ids: dict[str, int] = {}
        for mapping in mappings:
            root_urls_to_ids[mapping["url"]] = mapping["id"]

        results: list[URLMapping] = [
            URLMapping(
                url=mapping["url"],
                url_id=root_urls_to_ids.get(mapping["url"])
            ) for mapping in mappings
        ]

        return results