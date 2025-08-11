
from sqlalchemy import Select
from starlette.exceptions import HTTPException
from starlette.status import HTTP_400_BAD_REQUEST

from src.api.endpoints.review.enums import RejectionReason
from src.collectors.enums import URLStatus
from src.db.models.instantiations.url.core.sqlalchemy import URL
from src.db.models.instantiations.url.reviewing_user import ReviewingUserURL
from src.db.queries.base.builder import QueryBuilderBase


class RejectURLQueryBuilder(QueryBuilderBase):

    def __init__(
        self,
        url_id: int,
        user_id: int,
        rejection_reason: RejectionReason
    ):
        super().__init__()
        self.url_id = url_id
        self.user_id = user_id
        self.rejection_reason = rejection_reason

    async def run(self, session) -> None:

        query = (
            Select(URL)
            .where(URL.id == self.url_id)
        )

        url = await session.execute(query)
        url = url.scalars().first()

        match self.rejection_reason:
            case RejectionReason.INDIVIDUAL_RECORD:
                url.status = URLStatus.INDIVIDUAL_RECORD.value
            case RejectionReason.BROKEN_PAGE_404:
                url.status = URLStatus.NOT_FOUND.value
            case RejectionReason.NOT_RELEVANT:
                url.status = URLStatus.NOT_RELEVANT.value
            case _:
                raise HTTPException(
                    status_code=HTTP_400_BAD_REQUEST,
                    detail="Invalid rejection reason"
                )

        # Add rejecting user
        rejecting_user_url = ReviewingUserURL(
            user_id=self.user_id,
            url_id=self.url_id
        )

        session.add(rejecting_user_url)