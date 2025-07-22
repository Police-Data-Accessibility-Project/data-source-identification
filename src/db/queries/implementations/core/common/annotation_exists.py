"""
The annotation exists common table expression
Provides a set of boolean flags indicating whether a URL
has each kind of possible annotation
Each row should have the following columns:
- url_id
- UserRelevantSuggestion_exists
- UserRecordTypeSuggestion_exists
- UserUrlAgencySuggestion_exists
- UserAutoRelevantSuggestion_exists
- UserAutoRecordTypeSuggestion_exists
- UserAutoUrlAgencySuggestion_exists
"""

from typing import Any, Type

from sqlalchemy import case, func, Select, select

from src.collectors.enums import URLStatus
from src.db.constants import ALL_ANNOTATION_MODELS
from src.db.models.instantiations.url.core.sqlalchemy import URL
from src.db.models.mixins import URLDependentMixin
from src.db.queries.base.builder import QueryBuilderBase


class AnnotationExistsCTEQueryBuilder(QueryBuilderBase):

    @property
    def url_id(self):
        return self.query.c.url_id

    def get_exists_label(self, model: Type[URLDependentMixin]):
        return f"{model.__name__}_exists"

    def get_all(self) -> list[Any]:
        l = [self.url_id]
        for model in ALL_ANNOTATION_MODELS:
            label = self.get_exists_label(model)
            l.append(self.get(label))
        return l

    async def _annotation_exists_case(
        self,
    ):
        cases = []
        for model in ALL_ANNOTATION_MODELS:
            cases.append(
                case(
                    (
                        func.bool_or(model.url_id.is_not(None)), 1
                    ),
                    else_=0
                ).label(self.get_exists_label(model))
            )
        return cases

    async def _outer_join_models(self, query: Select):
        for model in ALL_ANNOTATION_MODELS:
            query = query.outerjoin(model)
        return query


    async def build(self) -> Any:
        annotation_exists_cases_all = await self._annotation_exists_case()
        anno_exists_query = select(
            URL.id.label("url_id"),
            *annotation_exists_cases_all
        )
        anno_exists_query = await self._outer_join_models(anno_exists_query)
        anno_exists_query = anno_exists_query.where(URL.outcome == URLStatus.PENDING.value)
        anno_exists_query = anno_exists_query.group_by(URL.id).cte("annotations_exist")
        self.query = anno_exists_query
