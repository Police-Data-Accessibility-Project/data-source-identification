from typing import Optional, Type

from sqlalchemy import case, select, func, Select, and_, desc, asc, FromClause
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.api.endpoints.review.dtos.get import GetNextURLForFinalReviewResponse, FinalReviewOptionalMetadata, \
    FinalReviewAnnotationInfo, FinalReviewBatchInfo
from src.collectors.enums import URLStatus
from src.core.tasks.operators.url_html.scraper.parser.util import convert_to_response_html_info
from src.db.dto_converter import DTOConverter
from src.db.dtos.url_html_content_info import URLHTMLContentInfo
from src.db.exceptions import FailedQueryException
from src.db.models.instantiations.confirmed_url_agency import ConfirmedURLAgency
from src.db.models.instantiations.url.suggestion.agency.auto import AutomatedUrlAgencySuggestion
from src.db.models.instantiations.url.suggestion.record_type.auto import AutoRecordTypeSuggestion
from src.db.models.instantiations.url.suggestion.agency.user import UserUrlAgencySuggestion
from src.db.models.instantiations.url.core import URL
from src.db.models.instantiations.url.suggestion.record_type.user import UserRecordTypeSuggestion
from src.db.models.instantiations.url.suggestion.relevant.auto import AutoRelevantSuggestion
from src.db.models.instantiations.url.suggestion.relevant.user import UserRelevantSuggestion
from src.db.models.mixins import URLDependentMixin
from src.db.queries.base.builder import QueryBuilderBase


TOTAL_DISTINCT_ANNOTATION_COUNT_LABEL = "total_distinct_annotation_count"

class GetNextURLForFinalReviewQueryBuilder(QueryBuilderBase):

    def __init__(self, batch_id: Optional[int] = None):
        super().__init__()
        self.batch_id = batch_id
        self.user_models = [
            UserRelevantSuggestion,
            UserRecordTypeSuggestion,
            UserUrlAgencySuggestion
        ]
        self.models = [
            AutoRelevantSuggestion,
            AutoRecordTypeSuggestion,
            AutomatedUrlAgencySuggestion,
            *self.user_models
        ]
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
            (URL.confirmed_agencies, ConfirmedURLAgency.agency)
        ]

    def get_exists_label(self, model: Type[URLDependentMixin]):
        return f"{model.__name__}_exists"

    async def _annotation_exists_case(
        self,
        models: list[Type[URLDependentMixin]]
    ):
        cases = []
        for model in models:
            cases.append(
                case(
                    (
                        func.bool_or(model.url_id != None), 1
                    ),
                    else_=0
                ).label(self.get_exists_label(model))
            )
        return cases

    async def _outer_join_models(self, query: Select, list_of_models: list[Type[URLDependentMixin]]):
        for model in list_of_models:
            query = query.outerjoin(model)
        return query

    def _get_where_exist_clauses(
        self,
        query: FromClause,
    ):
        where_clauses = []
        for model in self.user_models:
            label = self.get_exists_label(model)
            where_clause = getattr(query.c, label) == 1
            where_clauses.append(where_clause)
        return where_clauses

    def _build_base_query(self, anno_exists_query: FromClause, ):
        where_exist_clauses = self._get_where_exist_clauses(anno_exists_query)

        return (
            select(
                URL,
                self._sum_exists_query(anno_exists_query, self.models)
            )
            .select_from(anno_exists_query)
            .join(
                URL,
                URL.id == anno_exists_query.c.id
            )
            .where(
                and_(
                    URL.outcome == URLStatus.PENDING.value,
                    *where_exist_clauses
                )
            )
        )

    def _sum_exists_query(self, query, models: list[Type[URLDependentMixin]]):
        return sum(
            [getattr(query.c, self.get_exists_label(model)) for model in models]
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

        count_label = "count"
        count_reviewed_query = (
            select(
                URL.batch_id,
                func.count(URL.id).label(count_label)
            )
            .where(
                URL.outcome.in_(
                    [
                        URLStatus.VALIDATED.value,
                        URLStatus.NOT_RELEVANT.value,
                        URLStatus.SUBMITTED.value,
                        URLStatus.INDIVIDUAL_RECORD.value
                    ]
                ),
                URL.batch_id == self.batch_id
            )
            .group_by(URL.batch_id)
            .subquery("count_reviewed")
        )

        anno_exists_query = await self.get_anno_exists_query()
        count_ready_query = (
            select(
                URL.batch_id,
                func.count(URL.id).label(count_label)
            )
            .join(
                anno_exists_query,
                anno_exists_query.c.id == URL.id
            )
            .where(
                URL.batch_id == self.batch_id,
                URL.outcome == URLStatus.PENDING.value,
                *self._get_where_exist_clauses(
                    anno_exists_query
                )
            )
            .group_by(URL.batch_id)
            .subquery("count_ready")
        )

        full_query = (
            select(
                func.coalesce(count_reviewed_query.c[count_label], 0).label("count_reviewed"),
                func.coalesce(count_ready_query.c[count_label], 0).label("count_ready_for_review")
            )
            .select_from(
                count_reviewed_query.outerjoin(
                    count_ready_query,
                    count_reviewed_query.c.batch_id == count_ready_query.c.batch_id
                )
            )
        )

        raw_result = await session.execute(full_query)
        return FinalReviewBatchInfo(**raw_result.mappings().one())








    async def run(
        self,
        session: AsyncSession
    ) -> Optional[GetNextURLForFinalReviewResponse]:

        anno_exists_query = await self.get_anno_exists_query()

        url_query = self._build_base_query(anno_exists_query)
        url_query = await self._apply_batch_id_filter(url_query, self.batch_id)
        url_query = await self._apply_options(url_query)
        url_query = await self._apply_order_clause(url_query)
        url_query = url_query.limit(1)

        raw_result = await session.execute(url_query)
        row = raw_result.unique().first()

        if row is None:
            return None

        result: URL = row[0]

        html_content_infos = await self._extract_html_content_infos(result)
        optional_metadata = await self._extract_optional_metadata(result)

        batch_info = await self.get_batch_info(session)
        try:
            return GetNextURLForFinalReviewResponse(
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
        except Exception as e:
            raise FailedQueryException(f"Failed to convert result for url id {result.id} to response") from e

    async def get_anno_exists_query(self):
        annotation_exists_cases_all = await self._annotation_exists_case(self.models)
        anno_exists_query = select(
            URL.id,
            *annotation_exists_cases_all
        )
        anno_exists_query = await self._outer_join_models(anno_exists_query, self.models)
        anno_exists_query = anno_exists_query.where(URL.outcome == URLStatus.PENDING.value)
        anno_exists_query = anno_exists_query.group_by(URL.id).cte("annotations_exist")
        return anno_exists_query








