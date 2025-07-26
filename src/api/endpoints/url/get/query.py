from sqlalchemy import select, exists
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.api.endpoints.url.get.dto import GetURLsResponseInfo, GetURLsResponseErrorInfo, GetURLsResponseInnerInfo
from src.collectors.enums import URLStatus
from src.db.client.helpers import add_standard_limit_and_offset
from src.db.models.instantiations.url.core.sqlalchemy import URL
from src.db.models.instantiations.url.error_info.sqlalchemy import URLErrorInfo
from src.db.queries.base.builder import QueryBuilderBase


class GetURLsQueryBuilder(QueryBuilderBase):

    def __init__(
        self,
        page: int,
        errors: bool
    ):
        super().__init__()
        self.page = page
        self.errors = errors

    async def run(self, session: AsyncSession) -> GetURLsResponseInfo:
        statement = select(URL).options(
            selectinload(URL.error_info),
            selectinload(URL.batch)
        ).order_by(URL.id)
        if self.errors:
            # Only return URLs with errors
            statement = statement.where(
                exists(
                    select(URLErrorInfo).where(URLErrorInfo.url_id == URL.id)
                )
            )
        add_standard_limit_and_offset(statement, self.page)
        execute_result = await session.execute(statement)
        all_results = execute_result.scalars().all()
        final_results = []
        for result in all_results:
            error_results = []
            for error in result.error_info:
                error_result = GetURLsResponseErrorInfo(
                    id=error.id,
                    error=error.error,
                    updated_at=error.updated_at
                )
                error_results.append(error_result)
            final_results.append(
                GetURLsResponseInnerInfo(
                    id=result.id,
                    batch_id=result.batch.id if result.batch is not None else None,
                    url=result.url,
                    status=URLStatus(result.outcome),
                    collector_metadata=result.collector_metadata,
                    updated_at=result.updated_at,
                    created_at=result.created_at,
                    errors=error_results,
                )
            )

        return GetURLsResponseInfo(
            urls=final_results,
            count=len(final_results)
        )