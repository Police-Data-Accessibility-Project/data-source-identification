from typing import Sequence

from sqlalchemy import select, Row
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.collectors.enums import URLStatus
from src.core.tasks.url.operators.auto_relevant.models.tdo import URLRelevantTDO
from src.db.models.instantiations.url.html.compressed.sqlalchemy import URLCompressedHTML
from src.db.models.instantiations.url.core.sqlalchemy import URL
from src.db.models.instantiations.url.suggestion.relevant.auto.sqlalchemy import AutoRelevantSuggestion
from src.db.queries.base.builder import QueryBuilderBase
from src.db.statement_composer import StatementComposer
from src.db.utils.compression import decompress_html


class GetAutoRelevantTDOsQueryBuilder(QueryBuilderBase):

    def __init__(self):
        super().__init__()

    async def run(self, session: AsyncSession) -> list[URLRelevantTDO]:
        query = (
            select(
                URL
            )
            .options(
                selectinload(URL.compressed_html)
            )
            .join(URLCompressedHTML)
            .where(
                URL.status == URLStatus.PENDING.value,
            )
        )
        query = StatementComposer.exclude_urls_with_extant_model(
            query,
            model=AutoRelevantSuggestion
        )
        query = query.limit(100).order_by(URL.id)
        raw_result = await session.execute(query)
        urls: Sequence[Row[URL]] = raw_result.unique().scalars().all()
        tdos = []
        for url in urls:
            tdos.append(
                URLRelevantTDO(
                    url_id=url.id,
                    html=decompress_html(url.compressed_html.compressed_html),
                )
            )

        return tdos

