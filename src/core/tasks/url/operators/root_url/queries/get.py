from typing import override

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tasks.url.operators.root_url.queries._shared.urls_without_root_id import URLS_WITHOUT_ROOT_ID_QUERY
from src.db.dtos.url.mapping import URLMapping
from src.db.models.impl.flag.root_url.sqlalchemy import FlagRootURL
from src.db.models.impl.link.urls_root_url.sqlalchemy import LinkURLRootURL
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.queries.base.builder import QueryBuilderBase

from src.db.helpers.session import session_helper as sh

class GetURLsForRootURLTaskQueryBuilder(QueryBuilderBase):

    @override
    async def run(self, session: AsyncSession) -> list[URLMapping]:
        query = (
            URLS_WITHOUT_ROOT_ID_QUERY
        )
        mappings = await sh.mappings(session, query=query)
        return [
            URLMapping(
                url_id=mapping["id"],
                url=mapping["url"]
            ) for mapping in mappings
        ]