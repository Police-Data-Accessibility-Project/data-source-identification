from typing import Any, Generic, Optional

from sqlalchemy import FromClause, ColumnClause
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.helpers.session import session_helper as sh
from src.db.types import LabelsType


class QueryBuilderBase(Generic[LabelsType]):

    def __init__(self, labels: LabelsType | None = None):
        self.query: FromClause | None = None
        self.labels = labels

    def get(self, key: str) -> ColumnClause:
        return getattr(self.query.c, key)

    def get_all(self) -> list[Any]:
        results = []
        for label in self.labels.get_all_labels():
            results.append(self.get(label))
        return results

    def __getitem__(self, key: str) -> ColumnClause:
        return self.get(key)

    async def build(self) -> Any:
        raise NotImplementedError

    async def run(self, session: AsyncSession) -> Any:
        raise NotImplementedError

    @staticmethod
    def compile(query) -> Any:
        return sh.compile_to_sql(query)
