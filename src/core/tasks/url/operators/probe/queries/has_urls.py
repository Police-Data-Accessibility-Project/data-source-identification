from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import override, final

from src.db.helpers.session import session_helper as sh
from src.db.models.instantiations.url.core.sqlalchemy import URL
from src.db.models.instantiations.url.web_metadata.sqlalchemy import UrlWebMetadata
from src.db.queries.base.builder import QueryBuilderBase

@final
class HasURLsWithoutProbeQueryBuilder(QueryBuilderBase):

    @override
    async def run(self, session: AsyncSession) -> bool:
        query = (
            select(
                URL.id
            )
            .outerjoin(
                UrlWebMetadata,
                URL.id == UrlWebMetadata.url_id
            )
            .where(
                UrlWebMetadata.id.is_(None)
            )
        )
        return await sh.has_results(session, query=query)
