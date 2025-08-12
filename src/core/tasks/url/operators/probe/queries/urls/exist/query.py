from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tasks.url.operators.probe.queries.urls.exist.model import UrlExistsResult
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.queries.base.builder import QueryBuilderBase
from src.db.helpers.session import session_helper as sh

class URLsExistInDBQueryBuilder(QueryBuilderBase):
    """Checks if URLs exist in the database."""

    def __init__(self, urls: list[str]):
        super().__init__()
        self.urls = urls

    async def run(self, session: AsyncSession) -> list[UrlExistsResult]:
        query = select(URL.id, URL.url).where(URL.url.in_(self.urls))
        db_mappings = await sh.mappings(session, query=query)

        url_to_id_map: dict[str, int] = {
            row["url"]: row["id"]
            for row in db_mappings
        }
        return [
            UrlExistsResult(
                url=url,
                url_id=url_to_id_map.get(url)
            ) for url in self.urls
        ]