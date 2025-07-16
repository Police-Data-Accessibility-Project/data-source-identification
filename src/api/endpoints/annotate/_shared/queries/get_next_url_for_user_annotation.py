from sqlalchemy import select, not_, exists
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import QueryableAttribute, joinedload

from src.collectors.enums import URLStatus
from src.core.enums import SuggestedStatus
from src.db.client.types import UserSuggestionModel
from src.db.models.instantiations.url.core import URL
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
        url_query = (
            select(
                URL,
            )
            .where(URL.outcome == URLStatus.PENDING.value)
            # URL must not have user suggestion
            .where(
                StatementComposer.user_suggestion_not_exists(self.user_suggestion_model_to_exclude)
            )
        )

        if self.check_if_annotated_not_relevant:
            url_query = url_query.where(
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

        if self.batch_id is not None:
            url_query = url_query.where(URL.batch_id == self.batch_id)

        url_query = url_query.options(
            joinedload(self.auto_suggestion_relationship),
            joinedload(URL.html_content)
        ).limit(1)

        raw_result = await session.execute(url_query)

        return raw_result.unique().scalars().one_or_none()