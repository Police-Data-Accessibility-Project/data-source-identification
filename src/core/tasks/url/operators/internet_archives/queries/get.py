from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.dtos.url.mapping import URLMapping
from src.db.models.impl.flag.checked_for_ia.sqlalchemy import FlagURLCheckedForInternetArchives
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.queries.base.builder import QueryBuilderBase

from src.db.helpers.session import session_helper as sh

class GetURLsForInternetArchivesTaskQueryBuilder(QueryBuilderBase):

    async def run(self, session: AsyncSession) -> list[URLMapping]:
        query = (
            select(
                URL.id,
                URL.url
            )
            .outerjoin(
                FlagURLCheckedForInternetArchives,
                URL.id == FlagURLCheckedForInternetArchives.url_id
            )
            .where(FlagURLCheckedForInternetArchives.url_id.is_(None))
            .limit(100)
        )

        db_mappings = await sh.mappings(session, query=query)
        return [
            URLMapping(
                url_id=mapping["id"],
                url=mapping["url"]
            ) for mapping in db_mappings
        ]
