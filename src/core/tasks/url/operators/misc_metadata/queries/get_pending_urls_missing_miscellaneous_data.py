from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.collectors.enums import CollectorType
from src.core.tasks.url.operators.misc_metadata.tdo import URLMiscellaneousMetadataTDO, URLHTMLMetadataInfo
from src.db.models.impl.url.html.content.enums import HTMLContentType
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.queries.base.builder import QueryBuilderBase
from src.db.statement_composer import StatementComposer


class GetPendingURLsMissingMiscellaneousDataQueryBuilder(QueryBuilderBase):


    async def run(self, session: AsyncSession) -> list[URLMiscellaneousMetadataTDO]:
        query = StatementComposer.pending_urls_missing_miscellaneous_metadata_query()
        query = (
            query.options(
                selectinload(URL.batch),
                selectinload(URL.html_content)
            ).limit(100).order_by(URL.id)
        )

        scalar_result = await session.scalars(query)
        all_results = scalar_result.all()
        final_results = []
        for result in all_results:
            tdo = URLMiscellaneousMetadataTDO(
                url_id=result.id,
                collector_metadata=result.collector_metadata or {},
                collector_type=CollectorType(result.batch.strategy),
            )
            html_info = URLHTMLMetadataInfo()
            for html_content in result.html_content:
                if html_content.content_type == HTMLContentType.TITLE.value:
                    html_info.title = html_content.content
                elif html_content.content_type == HTMLContentType.DESCRIPTION.value:
                    html_info.description = html_content.content
            tdo.html_metadata_info = html_info
            final_results.append(tdo)
        return final_results
