from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from src.db.models.instantiations.duplicate.pydantic.info import DuplicateInfo
from src.db.models.instantiations.batch.sqlalchemy import Batch
from src.db.models.instantiations.duplicate.sqlalchemy import Duplicate
from src.db.models.instantiations.link.batch_url import LinkBatchURL
from src.db.models.instantiations.url.core.sqlalchemy import URL
from src.db.queries.base.builder import QueryBuilderBase


class GetDuplicatesByBatchIDQueryBuilder(QueryBuilderBase):

    def __init__(
        self,
        batch_id: int,
        page: int
    ):
        super().__init__()
        self.batch_id = batch_id
        self.page = page

    async def run(self, session: AsyncSession) -> list[DuplicateInfo]:
        original_batch = aliased(Batch)
        duplicate_batch = aliased(Batch)

        query = (
            Select(
                URL.url.label("source_url"),
                URL.id.label("original_url_id"),
                duplicate_batch.id.label("duplicate_batch_id"),
                duplicate_batch.parameters.label("duplicate_batch_parameters"),
                original_batch.id.label("original_batch_id"),
                original_batch.parameters.label("original_batch_parameters"),
            )
            .select_from(Duplicate)
            .join(URL, Duplicate.original_url_id == URL.id)
            .join(duplicate_batch, Duplicate.batch_id == duplicate_batch.id)
            .join(LinkBatchURL, URL.id == LinkBatchURL.url_id)
            .join(original_batch, LinkBatchURL.batch_id == original_batch.id)
            .filter(duplicate_batch.id == self.batch_id)
            .limit(100)
            .offset((self.page - 1) * 100)
        )
        raw_results = await session.execute(query)
        results = raw_results.all()
        final_results = []
        for result in results:
            final_results.append(
                DuplicateInfo(
                    source_url=result.source_url,
                    duplicate_batch_id=result.duplicate_batch_id,
                    duplicate_metadata=result.duplicate_batch_parameters,
                    original_batch_id=result.original_batch_id,
                    original_metadata=result.original_batch_parameters,
                    original_url_id=result.original_url_id
                )
            )
        return final_results
