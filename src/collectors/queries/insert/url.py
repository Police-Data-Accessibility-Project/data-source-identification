from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.instantiations.link.batch_url import LinkBatchURL
from src.db.models.instantiations.url.core.pydantic.info import URLInfo
from src.db.models.instantiations.url.core.sqlalchemy import URL
from src.db.queries.base.builder import QueryBuilderBase


class InsertURLQueryBuilder(QueryBuilderBase):


    def __init__(self, url_info: URLInfo):
        super().__init__()
        self.url_info = url_info

    async def run(self, session: AsyncSession) -> int:
        """Insert a new URL into the database."""
        url_entry = URL(
            url=self.url_info.url,
            collector_metadata=self.url_info.collector_metadata,
            status=self.url_info.status.value,
            source=self.url_info.source
        )
        if self.url_info.created_at is not None:
            url_entry.created_at = self.url_info.created_at
        session.add(url_entry)
        await session.flush()
        link = LinkBatchURL(
            batch_id=self.url_info.batch_id,
            url_id=url_entry.id
        )
        session.add(link)
        return url_entry.id