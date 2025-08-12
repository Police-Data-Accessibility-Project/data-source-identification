from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.collectors.enums import URLStatus
from src.core.tasks.scheduled.impl.huggingface.queries.get.convert import convert_url_status_to_relevant, \
    convert_fine_to_coarse_record_type
from src.core.tasks.scheduled.impl.huggingface.queries.get.model import GetForLoadingToHuggingFaceOutput
from src.db.models.impl.url.html.compressed.sqlalchemy import URLCompressedHTML
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.queries.base.builder import QueryBuilderBase
from src.db.utils.compression import decompress_html
from src.db.helpers.session import session_helper as sh

class GetForLoadingToHuggingFaceQueryBuilder(QueryBuilderBase):


    async def run(self, session: AsyncSession) -> list[GetForLoadingToHuggingFaceOutput]:
        label_url_id = 'url_id'
        label_url = 'url'
        label_url_status = 'url_status'
        label_record_type_fine = 'record_type_fine'
        label_html = 'html'


        query = (
            select(
                URL.id.label(label_url_id),
                URL.url.label(label_url),
                URL.status.label(label_url_status),
                URL.record_type.label(label_record_type_fine),
                URLCompressedHTML.compressed_html.label(label_html)
            )
            .join(
                URLCompressedHTML,
                URL.id == URLCompressedHTML.url_id
            )
            .where(
                URL.status.in_([
                    URLStatus.VALIDATED,
                    URLStatus.NOT_RELEVANT,
                    URLStatus.SUBMITTED
                ])
            )
        )
        db_results = await sh.mappings(
            session=session,
            query=query
        )
        final_results = []
        for result in db_results:
            output = GetForLoadingToHuggingFaceOutput(
                url_id=result[label_url_id],
                url=result[label_url],
                relevant=convert_url_status_to_relevant(result[label_url_status]),
                record_type_fine=result[label_record_type_fine],
                record_type_coarse=convert_fine_to_coarse_record_type(
                    result[label_record_type_fine]
                ),
                html=decompress_html(result[label_html])
            )
            final_results.append(output)

        return final_results
