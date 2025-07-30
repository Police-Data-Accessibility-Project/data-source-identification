from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import count

from src.collectors.enums import URLStatus
from src.db.helpers.session import session_helper as sh
from src.db.models.instantiations.state.huggingface import HuggingFaceUploadState
from src.db.models.instantiations.url.compressed_html import URLCompressedHTML
from src.db.models.instantiations.url.core.sqlalchemy import URL


class CheckValidURLsUpdatedRequester:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def latest_upload(self) -> datetime:
        query = (
            select(
                HuggingFaceUploadState.last_upload_at
            )
        )
        return await sh.scalar(
            session=self.session,
            query=query
        )

    async def has_valid_urls(self, last_upload_at: datetime | None) -> bool:
        query = (
            select(count(URL.id))
            .join(
                URLCompressedHTML,
                URL.id == URLCompressedHTML.url_id
            )
            .where(
                URL.outcome.in_(
                    [
                        URLStatus.VALIDATED,
                        URLStatus.NOT_RELEVANT.value,
                        URLStatus.SUBMITTED.value,
                    ]
                ),
            )
        )
        if last_upload_at is not None:
            query = query.where(URL.updated_at > last_upload_at)
        url_count = await sh.scalar(
            session=self.session,
            query=query
        )
        return url_count > 0
