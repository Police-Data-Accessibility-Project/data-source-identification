from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tasks.scheduled.impl.huggingface.queries.check.requester import CheckValidURLsUpdatedRequester
from src.db.queries.base.builder import QueryBuilderBase


class CheckValidURLsUpdatedQueryBuilder(QueryBuilderBase):

    async def run(self, session: AsyncSession) -> bool:
        requester = CheckValidURLsUpdatedRequester(session=session)
        latest_upload = await requester.latest_upload()
        return await requester.has_valid_urls(latest_upload)


