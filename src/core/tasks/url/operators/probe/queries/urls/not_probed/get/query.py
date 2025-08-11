from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import override, final

from src.util.clean import clean_url
from src.db.dtos.url.mapping import URLMapping
from src.db.models.instantiations.url.core.sqlalchemy import URL
from src.db.models.instantiations.url.web_metadata.sqlalchemy import URLWebMetadata
from src.db.helpers.session import session_helper as sh
from src.db.queries.base.builder import QueryBuilderBase


@final
class GetURLsWithoutProbeQueryBuilder(QueryBuilderBase):

    @override
    async def run(self, session: AsyncSession) -> list[URLMapping]:
        query = (
            select(
                URL.id.label("url_id"),
                URL.url
            )
            .outerjoin(
                URLWebMetadata,
                URL.id == URLWebMetadata.url_id
            )
            .where(
                URLWebMetadata.id.is_(None)
            )
            .limit(500)
        )
        db_mappings = await sh.mappings(session, query=query)
        return [
            URLMapping(
                url_id=mapping["url_id"],
                url=clean_url(mapping["url"])
            ) for mapping in db_mappings
        ]