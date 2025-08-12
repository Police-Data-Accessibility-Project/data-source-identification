from typing import List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.endpoints.annotate.dtos.shared.batch import AnnotationBatchInfo
from src.collectors.enums import URLStatus
from src.db.models.impl.link.batch_url import LinkBatchURL
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.queries.base.builder import QueryBuilderBase
from src.db.statement_composer import StatementComposer
from src.db.types import UserSuggestionType


class GetAnnotationBatchInfoQueryBuilder(QueryBuilderBase):

    def __init__(
        self,
        batch_id: int | None,
        models: List[UserSuggestionType]
    ):
        super().__init__()
        self.batch_id = batch_id
        self.models = models

    async def run(
        self,
        session: AsyncSession
    ) -> AnnotationBatchInfo | None:
        if self.batch_id is None:
            return None

        sc = StatementComposer
        include_queries = [
            sc.user_suggestion_exists(model)
            for model in self.models
        ]

        select_url = (
            select(func.count(URL.id))
            .join(LinkBatchURL)
        )

        common_where_clause = [
            URL.status == URLStatus.PENDING.value,
            LinkBatchURL.batch_id == self.batch_id,
        ]

        annotated_query = (
            select_url
            .where(
                *common_where_clause,
                *include_queries,
            )
        )

        exclude_queries = [
            sc.user_suggestion_not_exists(model)
            for model in self.models
        ]

        not_annotated_query = (
            select_url
            .where(
                *common_where_clause,
                *exclude_queries,
            )
        )

        annotated_result_raw = await session.execute(annotated_query)
        annotated_result = annotated_result_raw.scalars().one_or_none()
        not_annotated_result_raw = await session.execute(not_annotated_query)
        not_annotated_result = not_annotated_result_raw.scalars().one_or_none()

        return AnnotationBatchInfo(
            count_annotated=annotated_result,
            count_not_annotated=not_annotated_result,
            total_urls=annotated_result + not_annotated_result
        )