from typing import Optional, Type

from sqlalchemy import FromClause, select, and_, Select, desc, asc, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.api.endpoints.review.next.dto import FinalReviewOptionalMetadata, FinalReviewBatchInfo, \
    GetNextURLForFinalReviewOuterResponse, GetNextURLForFinalReviewResponse, FinalReviewAnnotationInfo
from src.collectors.enums import URLStatus
from src.core.tasks.url.operators.html.scraper.parser.util import convert_to_response_html_info
from src.db.constants import USER_ANNOTATION_MODELS
from src.db.dto_converter import DTOConverter
from src.db.dtos.url.html_content import URLHTMLContentInfo
from src.db.exceptions import FailedQueryException
from src.db.models.instantiations.batch.sqlalchemy import Batch
from src.db.models.instantiations.link.batch_url import LinkBatchURL
from src.db.models.instantiations.link.url_agency.sqlalchemy import LinkURLAgency
from src.db.models.instantiations.url.core.sqlalchemy import URL
from src.db.models.instantiations.url.suggestion.agency.auto import AutomatedUrlAgencySuggestion
from src.db.models.instantiations.url.suggestion.agency.user import UserUrlAgencySuggestion
from src.db.models.mixins import URLDependentMixin
from src.db.queries.base.builder import QueryBuilderBase
from src.db.queries.implementations.core.common.annotation_exists import AnnotationExistsCTEQueryBuilder

TOTAL_DISTINCT_ANNOTATION_COUNT_LABEL = "total_distinct_annotation_count"


class GetNextURLForFinalReviewQueryBuilder(QueryBuilderBase):

    def __init__(self, batch_id: Optional[int] = None):
        super().__init__()
        self.batch_id = batch_id
        self.anno_exists_builder = AnnotationExistsCTEQueryBuilder()
        # The below relationships are joined directly to the URL
        self.single_join_relationships = [
            URL.html_content,
            URL.auto_record_type_suggestion,
            URL.auto_relevant_suggestion,
            URL.user_relevant_suggestion,
            URL.user_record_type_suggestion,
            URL.optional_data_source_metadata,
        ]
        # The below relationships are joined to entities that are joined to the URL
        self.double_join_relationships = [
            (URL.automated_agency_suggestions, AutomatedUrlAgencySuggestion.agency),
            (URL.user_agency_suggestion, UserUrlAgencySuggestion.agency),
            (URL.confirmed_agencies, LinkURLAgency.agency)
        ]

        self.count_label = "count"

    def _get_where_exist_clauses(
        self,
        query: FromClause,
    ):
        where_clauses = []
        for model in USER_ANNOTATION_MODELS:
            label = self.anno_exists_builder.get_exists_label(model)
            where_clause = getattr(query.c, label) == 1
            where_clauses.append(where_clause)
        return where_clauses

    def _build_base_query(
        self,
        anno_exists_query: FromClause,
    ) -> Select:
        builder = self.anno_exists_builder
        where_exist_clauses = self._get_where_exist_clauses(
            builder.query
        )

        query = (
            select(
                URL,
                self._sum_exists_query(anno_exists_query, USER_ANNOTATION_MODELS)
            )
            .select_from(anno_exists_query)
            .join(
                URL,
                URL.id == builder.url_id
            )
        )
        if self.batch_id is not None:
            query = (
                query.join(
                    LinkBatchURL
                )
                .where(
                    LinkBatchURL.batch_id == self.batch_id
                )
            )

        query = (
            query.where(
                and_(
                    URL.status == URLStatus.PENDING.value,
                    *where_exist_clauses
                )
            )
        )
        return query


    def _sum_exists_query(self, query, models: list[Type[URLDependentMixin]]):
        return sum(
            [getattr(query.c, self.anno_exists_builder.get_exists_label(model)) for model in models]
        ).label(TOTAL_DISTINCT_ANNOTATION_COUNT_LABEL)


    async def _apply_batch_id_filter(self, url_query: Select, batch_id: Optional[int]):
        if batch_id is None:
            return url_query
        return url_query.where(URL.batch_id == batch_id)

    async def _apply_options(
        self,
        url_query: Select
    ):
        return url_query.options(
            *[
                joinedload(relationship)
                for relationship in self.single_join_relationships
            ],
            *[
                joinedload(primary).joinedload(secondary)
                for primary, secondary in self.double_join_relationships
            ]
        )

    async def _apply_order_clause(self, url_query: Select):
        return url_query.order_by(
            desc(TOTAL_DISTINCT_ANNOTATION_COUNT_LABEL),
            asc(URL.id)
        )

    async def _extract_html_content_infos(self, url: URL) -> list[URLHTMLContentInfo]:
        html_content = url.html_content
        html_content_infos = [
            URLHTMLContentInfo(**html_info.__dict__)
            for html_info in html_content
        ]
        return html_content_infos

    async def _extract_optional_metadata(self, url: URL) -> FinalReviewOptionalMetadata:
        if url.optional_data_source_metadata is None:
            return FinalReviewOptionalMetadata()
        return FinalReviewOptionalMetadata(
            record_formats=url.optional_data_source_metadata.record_formats,
            data_portal_type=url.optional_data_source_metadata.data_portal_type,
            supplying_entity=url.optional_data_source_metadata.supplying_entity
        )

    async def get_batch_info(self, session: AsyncSession) -> Optional[FinalReviewBatchInfo]:
        if self.batch_id is None:
            return None

        count_reviewed_query = await self.get_count_reviewed_query()

        count_ready_query = await self.get_count_ready_query()

        full_query = (
            select(
                func.coalesce(count_reviewed_query.c[self.count_label], 0).label("count_reviewed"),
                func.coalesce(count_ready_query.c[self.count_label], 0).label("count_ready_for_review")
            )
            .select_from(
                count_ready_query.outerjoin(
                    count_reviewed_query,
                    count_reviewed_query.c.batch_id == count_ready_query.c.batch_id
                )
            )
        )

        raw_result = await session.execute(full_query)
        return FinalReviewBatchInfo(**raw_result.mappings().one())

    async def get_count_ready_query(self):
        builder = self.anno_exists_builder
        count_ready_query = (
            select(
                LinkBatchURL.batch_id,
                func.count(URL.id).label(self.count_label)
            )
            .select_from(LinkBatchURL)
            .join(URL)
            .join(
                builder.query,
                builder.url_id == URL.id
            )
            .where(
                LinkBatchURL.batch_id == self.batch_id,
                URL.status == URLStatus.PENDING.value,
                *self._get_where_exist_clauses(
                    builder.query
                )
            )
            .group_by(LinkBatchURL.batch_id)
            .subquery("count_ready")
        )
        return count_ready_query

    async def get_count_reviewed_query(self):
        count_reviewed_query = (
            select(
                Batch.id.label("batch_id"),
                func.count(URL.id).label(self.count_label)
            )
            .select_from(Batch)
            .join(LinkBatchURL)
            .outerjoin(URL, URL.id == LinkBatchURL.url_id)
            .where(
                URL.status.in_(
                    [
                        URLStatus.VALIDATED.value,
                        URLStatus.NOT_RELEVANT.value,
                        URLStatus.SUBMITTED.value,
                        URLStatus.INDIVIDUAL_RECORD.value
                    ]
                ),
                LinkBatchURL.batch_id == self.batch_id
            )
            .group_by(Batch.id)
            .subquery("count_reviewed")
        )
        return count_reviewed_query

    async def run(
        self,
        session: AsyncSession
    ) -> GetNextURLForFinalReviewOuterResponse:
        await self.anno_exists_builder.build()

        url_query = await self.build_url_query()

        raw_result = await session.execute(url_query.limit(1))
        row = raw_result.unique().first()

        if row is None:
            return GetNextURLForFinalReviewOuterResponse(
                next_source=None,
                remaining=0
            )

        count_query = (
            select(
                func.count()
            ).select_from(url_query.subquery("count"))
        )
        remaining_result = (await session.execute(count_query)).scalar()


        result: URL = row[0]

        html_content_infos = await self._extract_html_content_infos(result)
        optional_metadata = await self._extract_optional_metadata(result)

        batch_info = await self.get_batch_info(session)
        try:

            next_source = GetNextURLForFinalReviewResponse(
                id=result.id,
                url=result.url,
                html_info=convert_to_response_html_info(html_content_infos),
                name=result.name,
                description=result.description,
                annotations=FinalReviewAnnotationInfo(
                    relevant=DTOConverter.final_review_annotation_relevant_info(
                        user_suggestion=result.user_relevant_suggestion,
                        auto_suggestion=result.auto_relevant_suggestion
                    ),
                    record_type=DTOConverter.final_review_annotation_record_type_info(
                        user_suggestion=result.user_record_type_suggestion,
                        auto_suggestion=result.auto_record_type_suggestion
                    ),
                    agency=DTOConverter.final_review_annotation_agency_info(
                        automated_agency_suggestions=result.automated_agency_suggestions,
                        user_agency_suggestion=result.user_agency_suggestion,
                        confirmed_agencies=result.confirmed_agencies
                    )
                ),
                optional_metadata=optional_metadata,
                batch_info=batch_info
            )
            return GetNextURLForFinalReviewOuterResponse(
                next_source=next_source,
                remaining=remaining_result
            )
        except Exception as e:
            raise FailedQueryException(f"Failed to convert result for url id {result.id} to response") from e

    async def build_url_query(self):
        anno_exists_query = self.anno_exists_builder.query
        url_query = self._build_base_query(anno_exists_query)
        url_query = await self._apply_options(url_query)
        url_query = await self._apply_order_clause(url_query)

        return url_query
