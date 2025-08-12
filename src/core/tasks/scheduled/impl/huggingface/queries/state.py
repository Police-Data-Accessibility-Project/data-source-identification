from datetime import datetime

from sqlalchemy import delete, insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.impl.state.huggingface import HuggingFaceUploadState
from src.db.queries.base.builder import QueryBuilderBase


class SetHuggingFaceUploadStateQueryBuilder(QueryBuilderBase):

    def __init__(self, dt: datetime):
        super().__init__()
        self.dt = dt

    async def run(self, session: AsyncSession) -> None:
        # Delete entry if any exists
        await session.execute(
            delete(HuggingFaceUploadState)
        )
        # Insert entry
        await session.execute(
            insert(HuggingFaceUploadState).values(last_upload_at=self.dt)
        )
