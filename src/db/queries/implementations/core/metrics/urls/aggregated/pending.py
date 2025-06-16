from typing import Any, Type

from sqlalchemy import select, func, case
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.endpoints.metrics.dtos.get.urls.aggregated.pending import GetMetricsURLsAggregatedPendingResponseDTO
from src.collectors.enums import URLStatus
from src.db.models.instantiations.url.core import URL
from src.db.models.instantiations.url.suggestion.agency.user import UserUrlAgencySuggestion
from src.db.models.instantiations.url.suggestion.record_type.user import UserRecordTypeSuggestion
from src.db.models.instantiations.url.suggestion.relevant.user import UserRelevantSuggestion
from src.db.models.mixins import URLDependentMixin
from src.db.queries.base.builder import QueryBuilderBase
from src.db.queries.implementations.core.common.annotation_exists import AnnotationExistsCTEQueryBuilder

class PendingAnnotationExistsCTEQueryBuilder(AnnotationExistsCTEQueryBuilder):

    @property
    def has_user_relevant_annotation(self):
        return self.get_exists_for_model(UserRelevantSuggestion)

    @property
    def has_user_record_type_annotation(self):
        return self.get_exists_for_model(UserRecordTypeSuggestion)

    @property
    def has_user_agency_annotation(self):
        return self.get_exists_for_model(UserUrlAgencySuggestion)

    def get_exists_for_model(self, model: Type[URLDependentMixin]):
        return self.query.c[
            self.get_exists_label(model)
        ]

    async def build(self) -> Any:
        await super().build()

        self.query = (
            self.query
            .join(
                URL,
                URL.id == self.url_id
            )
            .where(
                URL.outcome == URLStatus.PENDING.value
            ).cte("pending")
        )



class GetMetricsURLSAggregatedPendingQueryBuilder(QueryBuilderBase):

    def __init__(self):
        super().__init__()
        self.pending_builder = PendingAnnotationExistsCTEQueryBuilder()

    async def get_flags(self, session: AsyncSession) -> Any:
        raise NotImplementedError

    async def run(self, session: AsyncSession) -> Any:
        await self.pending_builder.build()

        anno_breakdown_count_query = await self.get_anno_breakdown_count_query()
        count_breakdown_count_query = await self.get_count_breakdown_count_query()

        raw_result = await session.execute(anno_breakdown_count_query)
        # Anno breakdown has only one row,
        # with a column for each annotation type
        anno_breakdown_count = raw_result.mappings().one()

        raw_result = await session.execute(count_breakdown_count_query)

        # Count breakdown has multiple rows,
        # with a column for each count of annotations (0, 1, 2, 3)
        count_breakdown_count = raw_result.mappings().all()
        d = {f"annotations_{num}": 0 for num in range(4)}
        total_count = 0
        for row in count_breakdown_count:
            key = f"annotations_{row['true_count']}"
            d[key] = row["url_count"]
            total_count += row["url_count"]

        return GetMetricsURLsAggregatedPendingResponseDTO(
            all=total_count,
            relevant=anno_breakdown_count["relevant"],
            record_type=anno_breakdown_count["record_type"],
            agency=anno_breakdown_count["agency"],
            **d
        )


    async def get_count_breakdown_count_query(self):
        pb = self.pending_builder
        true_count = (
            case(pb.has_user_relevant_annotation, else_=0)
            + case(pb.has_user_record_type_annotation, else_=0)
            + case(pb.has_user_agency_annotation, else_=0)
        ).label("true_count")
        true_count_query = (
            select(
                true_count,
                func.count(func.count()).label("url_count")
            ).select_from(
                pb.query
            ).group_by(
                true_count
            ).order_by(
                true_count.asc()
            )
        )

        return true_count_query

    async def get_anno_breakdown_count_query(self):
        pb = self.pending_builder

        def func_sum(col, label):
            return func.sum(case((col, 1), else_=0)).label(label)

        anno_count_query = select(
            func_sum(pb.has_user_relevant_annotation, "has_user_relevant_annotation").label(
                "relevant"
                ),
            func_sum(pb.has_user_record_type_annotation, "has_user_record_type_annotation").label(
                "record_type"
                ),
            func_sum(pb.has_user_agency_annotation, "has_user_agency_annotation").label("agency"),
        ).select_from(pb.query)

        return anno_count_query

