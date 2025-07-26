from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.instantiations.url.core.pydantic import URLInfo
from src.db.models.instantiations.url.core.sqlalchemy import URL
from src.db.queries.base.builder import QueryBuilderBase
from src.db.statement_composer import StatementComposer


class GetPendingURLsWithoutHTMLDataQueryBuilder(QueryBuilderBase):

    async def run(self, session: AsyncSession) -> list[URLInfo]:
        statement = StatementComposer.pending_urls_without_html_data()
        statement = statement.limit(100).order_by(URL.id)
        scalar_result = await session.scalars(statement)
        url_results: list[URL] = scalar_result.all()

        final_results = []
        for url in url_results:
            url_info = URLInfo(
                id=url.id,
                batch_id=url.batch.id if url.batch is not None else None,
                url=url.url,
                collector_metadata=url.collector_metadata,
                outcome=url.outcome,
                created_at=url.created_at,
                updated_at=url.updated_at,
                name=url.name
            )
            final_results.append(url_info)

        return final_results
