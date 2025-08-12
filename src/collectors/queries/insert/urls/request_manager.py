from sqlalchemy.ext.asyncio import AsyncSession

from src.collectors.queries.get_url_info import GetURLInfoByURLQueryBuilder
from src.collectors.queries.insert.url import InsertURLQueryBuilder
from src.db.models.impl.duplicate.pydantic.insert import DuplicateInsertInfo
from src.db.models.impl.url.core.pydantic.info import URLInfo

from src.db.helpers.session import session_helper as sh


class InsertURLsRequestManager:

    def __init__(
        self,
        session: AsyncSession
    ):
        self.session = session

    async def insert_url(self, url_info: URLInfo) -> int:
        return await InsertURLQueryBuilder(
            url_info=url_info
        ).run(self.session)

    async def get_url_info_by_url(self, url: str) -> URLInfo | None:
        return await GetURLInfoByURLQueryBuilder(
            url=url
        ).run(self.session)

    async def insert_duplicates(
        self,
        duplicates: list[DuplicateInsertInfo]
    ) -> None:
        await sh.bulk_insert(self.session, models=duplicates)