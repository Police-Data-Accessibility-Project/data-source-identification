from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import override, final

from src.db.queries.base.builder import QueryBuilderBase

@final
class InsertURLMetadataInfoQueryBuilder(QueryBuilderBase):

    def __init__(
        self,

    ):

    @override
    async def run(self, session: AsyncSession) -> None:
