from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import override

from src.core.tasks.url.operators.root_url.queries._shared.urls_without_root_id import URLS_WITHOUT_ROOT_ID_QUERY
from src.db.dtos.url.mapping import URLMapping
from src.db.helpers.session import session_helper as sh
from src.db.queries.base.builder import QueryBuilderBase


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