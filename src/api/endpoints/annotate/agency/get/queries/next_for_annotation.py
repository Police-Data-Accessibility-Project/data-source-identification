from sqlalchemy import select, exists
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.endpoints.annotate._shared.queries.get_annotation_batch_info import GetAnnotationBatchInfoQueryBuilder
from src.api.endpoints.annotate.agency.get.dto import GetNextURLForAgencyAnnotationResponse, \
    GetNextURLForAgencyAnnotationInnerResponse
from src.api.endpoints.annotate.agency.get.queries.agency_suggestion import GetAgencySuggestionsQueryBuilder
from src.collectors.enums import URLStatus
from src.core.enums import SuggestedStatus
from src.core.tasks.url.operators.html.scraper.parser.util import convert_to_response_html_info
from src.db.dtos.url.mapping import URLMapping
from src.db.models.instantiations.link.batch_url import LinkBatchURL
from src.db.models.instantiations.link.url_agency.sqlalchemy import LinkURLAgency
from src.db.models.instantiations.url.core.sqlalchemy import URL
from src.db.models.instantiations.url.suggestion.agency.auto import AutomatedUrlAgencySuggestion
from src.db.models.instantiations.url.suggestion.agency.user import UserUrlAgencySuggestion
from src.db.models.instantiations.url.suggestion.relevant.user import UserRelevantSuggestion
from src.db.queries.base.builder import QueryBuilderBase
from src.db.queries.implementations.core.get.html_content_info import GetHTMLContentInfoQueryBuilder


class GetNextURLAgencyForAnnotationQueryBuilder(QueryBuilderBase):

    def __init__(
        self,
        batch_id: int | None,
        user_id: int
    ):
        super().__init__()
        self.batch_id = batch_id
        self.user_id = user_id

    async def run(
        self,
        session: AsyncSession
    ) -> GetNextURLForAgencyAnnotationResponse:
        """
        Retrieve URL for annotation
        The URL must
            not be a confirmed URL
            not have been annotated by this user
            have extant autosuggestions
        """
        # Select statement
        query = select(URL.id, URL.url)
        if self.batch_id is not None:
            query = query.join(LinkBatchURL).where(LinkBatchURL.batch_id == self.batch_id)

        # Must not have confirmed agencies
        query = query.where(
            URL.outcome == URLStatus.PENDING.value
        )


        # Must not have been annotated by a user
        query = (
            query.join(UserUrlAgencySuggestion, isouter=True)
            .where(
                ~exists(
                    select(UserUrlAgencySuggestion).
                    where(UserUrlAgencySuggestion.url_id == URL.id).
                    correlate(URL)
                )
            )
            # Must have extant autosuggestions
            .join(AutomatedUrlAgencySuggestion, isouter=True)
            .where(
                exists(
                    select(AutomatedUrlAgencySuggestion).
                    where(AutomatedUrlAgencySuggestion.url_id == URL.id).
                    correlate(URL)
                )
            )
            # Must not have confirmed agencies
            .join(LinkURLAgency, isouter=True)
            .where(
                ~exists(
                    select(LinkURLAgency).
                    where(LinkURLAgency.url_id == URL.id).
                    correlate(URL)
                )
            )
            # Must not have been marked as "Not Relevant" by this user
            .join(UserRelevantSuggestion, isouter=True)
            .where(
                ~exists(
                    select(UserRelevantSuggestion).
                    where(
                        (UserRelevantSuggestion.user_id == self.user_id) &
                        (UserRelevantSuggestion.url_id == URL.id) &
                        (UserRelevantSuggestion.suggested_status != SuggestedStatus.RELEVANT.value)
                    ).correlate(URL)
                )
            )
        ).limit(1)
        raw_result = await session.execute(query)
        results = raw_result.all()
        if len(results) == 0:
            return GetNextURLForAgencyAnnotationResponse(
                next_annotation=None
            )

        result = results[0]
        url_id = result[0]
        url = result[1]

        agency_suggestions = await GetAgencySuggestionsQueryBuilder(url_id=url_id).run(session)

        # Get HTML content info
        html_content_infos = await GetHTMLContentInfoQueryBuilder(url_id).run(session)
        response_html_info = convert_to_response_html_info(html_content_infos)

        return GetNextURLForAgencyAnnotationResponse(
            next_annotation=GetNextURLForAgencyAnnotationInnerResponse(
                url_info=URLMapping(
                    url=url,
                    url_id=url_id
                ),
                html_info=response_html_info,
                agency_suggestions=agency_suggestions,
                batch_info=await GetAnnotationBatchInfoQueryBuilder(
                    batch_id=self.batch_id,
                    models=[
                        UserUrlAgencySuggestion,
                    ]
                ).run(session)
            )
        )