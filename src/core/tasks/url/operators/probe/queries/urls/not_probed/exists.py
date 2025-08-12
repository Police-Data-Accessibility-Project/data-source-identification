from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import override, final

from src.db.helpers.session import session_helper as sh
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.impl.url.web_metadata.sqlalchemy import URLWebMetadata
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
                URLWebMetadata,
                URL.id == URLWebMetadata.url_id
            )
            .where(
                URLWebMetadata.id.is_(None)
            )
        )
        return await sh.has_results(session, query=query)
