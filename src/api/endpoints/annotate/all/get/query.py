from sqlalchemy import Select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.api.endpoints.annotate._shared.queries.get_annotation_batch_info import GetAnnotationBatchInfoQueryBuilder
from src.api.endpoints.annotate.agency.get.queries.agency_suggestion import GetAgencySuggestionsQueryBuilder
from src.api.endpoints.annotate.agency.get.queries.next_for_annotation import GetNextURLAgencyForAnnotationQueryBuilder
from src.api.endpoints.annotate.all.get.dto import GetNextURLForAllAnnotationResponse, \
    GetNextURLForAllAnnotationInnerResponse
from src.api.endpoints.annotate.relevance.get.dto import RelevanceAnnotationResponseInfo
from src.collectors.enums import URLStatus
from src.db.dto_converter import DTOConverter
from src.db.dtos.url.mapping import URLMapping
from src.db.models.instantiations.link.link_batch_urls import LinkBatchURL
from src.db.models.instantiations.url.core import URL
from src.db.models.instantiations.url.suggestion.agency.user import UserUrlAgencySuggestion
from src.db.models.instantiations.url.suggestion.record_type.user import UserRecordTypeSuggestion
from src.db.models.instantiations.url.suggestion.relevant.user import UserRelevantSuggestion
from src.db.queries.base.builder import QueryBuilderBase
from src.db.statement_composer import StatementComposer


class GetNextURLForAllAnnotationQueryBuilder(QueryBuilderBase):

    def __init__(
        self,
        batch_id: int | None
    ):
        super().__init__()
        self.batch_id = batch_id

    async def run(
        self,
        session: AsyncSession
    ) -> GetNextURLForAllAnnotationResponse:
        query = Select(URL)
        if self.batch_id is not None:
            query = query.join(LinkBatchURL).where(LinkBatchURL.batch_id == self.batch_id)
        query = (
            query
            .where(
                and_(
                    URL.outcome == URLStatus.PENDING.value,
                    StatementComposer.user_suggestion_not_exists(UserUrlAgencySuggestion),
                    StatementComposer.user_suggestion_not_exists(UserRecordTypeSuggestion),
                    StatementComposer.user_suggestion_not_exists(UserRelevantSuggestion),
                )
            )
        )


        load_options = [
            URL.html_content,
            URL.automated_agency_suggestions,
            URL.auto_relevant_suggestion,
            URL.auto_record_type_suggestion
        ]
        select_in_loads = [
            selectinload(load_option) for load_option in load_options
        ]

        # Add load options
        query = query.options(
            *select_in_loads
        )

        query = query.order_by(URL.id.asc()).limit(1)
        raw_results = await session.execute(query)
        url = raw_results.scalars().one_or_none()
        if url is None:
            return GetNextURLForAllAnnotationResponse(
                next_annotation=None
            )

        html_response_info = DTOConverter.html_content_list_to_html_response_info(
            url.html_content
        )

        if url.auto_relevant_suggestion is not None:
            auto_relevant = url.auto_relevant_suggestion
        else:
            auto_relevant = None

        if url.auto_record_type_suggestion is not None:
            auto_record_type = url.auto_record_type_suggestion.record_type
        else:
            auto_record_type = None

        agency_suggestions = await GetAgencySuggestionsQueryBuilder(url_id=url.id).run(session)

        return GetNextURLForAllAnnotationResponse(
            next_annotation=GetNextURLForAllAnnotationInnerResponse(
                url_info=URLMapping(
                    url_id=url.id,
                    url=url.url
                ),
                html_info=html_response_info,
                suggested_relevant=RelevanceAnnotationResponseInfo(
                    is_relevant=auto_relevant.relevant,
                    confidence=auto_relevant.confidence,
                    model_name=auto_relevant.model_name
                ) if auto_relevant is not None else None,
                suggested_record_type=auto_record_type,
                agency_suggestions=agency_suggestions,
                batch_info=await GetAnnotationBatchInfoQueryBuilder(
                    batch_id=self.batch_id,
                    models=[
                        UserUrlAgencySuggestion,
                    ]
                ).run(session)
            )
        )