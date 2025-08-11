from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from src.collectors.enums import URLStatus
from src.core.tasks.url.operators.submit_approved.tdo import SubmittedURLInfo
from src.db.models.instantiations.url.core.sqlalchemy import URL
from src.db.models.instantiations.url.data_source.sqlalchemy import URLDataSource
from src.db.queries.base.builder import QueryBuilderBase


class MarkURLsAsSubmittedQueryBuilder(QueryBuilderBase):

    def __init__(self, infos: list[SubmittedURLInfo]):
        super().__init__()
        self.infos = infos

    async def run(self, session: AsyncSession):
        for info in self.infos:
            url_id = info.url_id
            data_source_id = info.data_source_id

            query = (
                update(URL)
                .where(URL.id == url_id)
                .values(
                    status=URLStatus.SUBMITTED.value
                )
            )

            url_data_source_object = URLDataSource(
                url_id=url_id,
                data_source_id=data_source_id
            )
            if info.submitted_at is not None:
                url_data_source_object.created_at = info.submitted_at
            session.add(url_data_source_object)

            await session.execute(query)