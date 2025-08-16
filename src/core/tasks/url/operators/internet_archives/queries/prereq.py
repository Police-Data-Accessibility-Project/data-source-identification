from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.impl.flag.checked_for_ia.sqlalchemy import FlagURLCheckedForInternetArchives
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.queries.base.builder import QueryBuilderBase

from src.db.helpers.session import session_helper as sh

class CheckURLInternetArchivesTaskPrerequisitesQueryBuilder(QueryBuilderBase):

    async def run(self, session: AsyncSession) -> bool:
        query = (
            select(URL)
            .outerjoin(
                FlagURLCheckedForInternetArchives,
                URL.id == FlagURLCheckedForInternetArchives.url_id
            )
            .where(FlagURLCheckedForInternetArchives.url_id.is_(None))
            .limit(1)
        )
        result = await sh.one_or_none(session, query=query)
        return result is not None
