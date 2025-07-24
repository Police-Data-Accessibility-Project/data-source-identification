from sqlalchemy import select, not_, exists
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import QueryableAttribute, joinedload

from src.collectors.enums import URLStatus
from src.core.enums import SuggestedStatus
from src.db.client.types import UserSuggestionModel
from src.db.models.instantiations.link.batch_url import LinkBatchURL
from src.db.models.instantiations.url.core.sqlalchemy import URL
from src.db.models.instantiations.url.suggestion.relevant.user import UserRelevantSuggestion
from src.db.queries.base.builder import QueryBuilderBase
from src.db.statement_composer import StatementComposer


class GetNextURLForUserAnnotationQueryBuilder(QueryBuilderBase):

    def __init__(
        self,
        user_suggestion_model_to_exclude: UserSuggestionModel,
        auto_suggestion_relationship: QueryableAttribute,
        batch_id: int | None,
        check_if_annotated_not_relevant: bool = False
    ):
        super().__init__()
        self.check_if_annotated_not_relevant = check_if_annotated_not_relevant
        self.batch_id = batch_id
        self.user_suggestion_model_to_exclude = user_suggestion_model_to_exclude
        self.auto_suggestion_relationship = auto_suggestion_relationship

    async def run(self, session: AsyncSession):
        query = (
            select(
                URL,
            )
        )

        if self.batch_id is not None:
            query = (
                query
                .join(LinkBatchURL)
                .where(LinkBatchURL.batch_id == self.batch_id)
            )

        query = (
            query
            .where(URL.outcome == URLStatus.PENDING.value)
            # URL must not have user suggestion
            .where(
                StatementComposer.user_suggestion_not_exists(self.user_suggestion_model_to_exclude)
            )
        )

        if self.check_if_annotated_not_relevant:
            query = query.where(
                not_(
                    exists(
                        select(UserRelevantSuggestion)
                        .where(
                            UserRelevantSuggestion.url_id == URL.id,
                            UserRelevantSuggestion.suggested_status != SuggestedStatus.RELEVANT.value
                        )
                    )
                )
            )



        query = query.options(
            joinedload(self.auto_suggestion_relationship),
            joinedload(URL.html_content)
        ).limit(1)

        raw_result = await session.execute(query)

        return raw_result.unique().scalars().one_or_none()