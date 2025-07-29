from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.collectors.enums import URLStatus
from src.core.tasks.scheduled.huggingface.queries.get.convert import convert_url_status_to_relevant, \
    convert_fine_to_coarse_record_type
from src.core.tasks.scheduled.huggingface.queries.get.model import GetForLoadingToHuggingFaceOutput
from src.db.models.instantiations.url.compressed_html import URLCompressedHTML
from src.db.models.instantiations.url.core.sqlalchemy import URL
from src.db.queries.base.builder import QueryBuilderBase
from src.db.utils.compression import decompress_html
from src.db.helpers.session import session_helper as sh

class GetForLoadingToHuggingFaceQueryBuilder(QueryBuilderBase):


    async def run(self, session: AsyncSession) -> list[GetForLoadingToHuggingFaceOutput]:

        query = (
            select(
                URL.id.label('url_id'),
                URL.url,
                convert_url_status_to_relevant(URL.outcome),
                convert_fine_to_coarse_record_type(URL.outcome),
                URLCompressedHTML.compressed_html.label('html')
            )
            .join(
                URLCompressedHTML,
                URL.id == URLCompressedHTML.url_id
            )
            .where(
                URL.outcome.in_([
                    URLStatus.VALIDATED,
                    URLStatus.NOT_RELEVANT,
                    URLStatus.SUBMITTED
                ])
            )
        )
        db_results = await sh.scalars(
            session=session,
            query=query
        )
        final_results = []
        for result in db_results:
            output = GetForLoadingToHuggingFaceOutput(
                url_id=result.url_id,
                url=result.url,
                relevant=convert_url_status_to_relevant(result.outcome),
                record_type_fine=result.record_type,
                record_type_coarse=convert_fine_to_coarse_record_type(result.record_type),
                html=decompress_html(result.html)
            )
            final_results.append(output)

        return final_results
