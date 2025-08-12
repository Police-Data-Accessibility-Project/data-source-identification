from sqlalchemy.ext.asyncio import AsyncSession

from src.api.endpoints.annotate._shared.queries.get_annotation_batch_info import GetAnnotationBatchInfoQueryBuilder
from src.api.endpoints.annotate._shared.queries.get_next_url_for_user_annotation import \
    GetNextURLForUserAnnotationQueryBuilder
from src.api.endpoints.annotate.relevance.get.dto import GetNextRelevanceAnnotationResponseInfo, \
    RelevanceAnnotationResponseInfo
from src.db.dto_converter import DTOConverter
from src.db.dtos.url.mapping import URLMapping
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.impl.url.suggestion.agency.user import UserUrlAgencySuggestion
from src.db.models.impl.url.suggestion.relevant.user import UserRelevantSuggestion
from src.db.queries.base.builder import QueryBuilderBase


class GetNextUrlForRelevanceAnnotationQueryBuilder(QueryBuilderBase):

    def __init__(
        self,
        batch_id: int | None
    ):
        super().__init__()
        self.batch_id = batch_id

    async def run(
        self,
        session: AsyncSession
    ) -> GetNextRelevanceAnnotationResponseInfo | None:
        url = await GetNextURLForUserAnnotationQueryBuilder(
            user_suggestion_model_to_exclude=UserRelevantSuggestion,
            auto_suggestion_relationship=URL.auto_relevant_suggestion,
            batch_id=self.batch_id
        ).run(session)
        if url is None:
            return None

        # Next, get all HTML content for the URL
        html_response_info = DTOConverter.html_content_list_to_html_response_info(
            url.html_content
        )

        if url.auto_relevant_suggestion is not None:
            suggestion = url.auto_relevant_suggestion
        else:
            suggestion = None

        return GetNextRelevanceAnnotationResponseInfo(
            url_info=URLMapping(
                url=url.url,
                url_id=url.id
            ),
            annotation=RelevanceAnnotationResponseInfo(
                is_relevant=suggestion.relevant,
                confidence=suggestion.confidence,
                model_name=suggestion.model_name
            ) if suggestion else None,
            html_info=html_response_info,
            batch_info=await GetAnnotationBatchInfoQueryBuilder(
                batch_id=self.batch_id,
                models=[
                    UserUrlAgencySuggestion,
                ]
            ).run(session)
        )
