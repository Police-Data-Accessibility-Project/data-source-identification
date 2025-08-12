from typing_extensions import override

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tasks.url.operators.root_url.queries._shared.urls_without_root_id import URLS_WITHOUT_ROOT_ID_QUERY
from src.db.queries.base.builder import QueryBuilderBase

from src.db.helpers.session import session_helper as sh

class CheckPrereqsForRootURLTaskQueryBuilder(QueryBuilderBase):

    @override
    async def run(self, session: AsyncSession) -> bool:
        query = (
            URLS_WITHOUT_ROOT_ID_QUERY
            .limit(1)
        )
        result = await sh.one_or_none(session, query=query)
        return result is not None